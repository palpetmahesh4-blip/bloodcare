
from datetime import date, datetime
from sqlalchemy import text
from database import engine


BUCKETS = [
    "Expired",
    "Expires today",
    "Within 7 days",
    "Within 30 days",
    "Safe",
]


def bucket_for(days_left):
    if days_left < 0:
        return "Expired"
    if days_left == 0:
        return "Expires today"
    if days_left <= 7:
        return "Within 7 days"
    if days_left <= 30:
        return "Within 30 days"
    return "Safe"


def _to_date(value):
    """SQLite string/date ko Python date mein convert karta hai."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        # Normal SQLite date format: YYYY-MM-DD
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            pass

        # Fallback for other common datetime formats
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
        ):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

    raise ValueError(f"Invalid expiry date: {value}")


def get_expiry_units(bucket="All", blood_group="All"):
    today = date.today()

    sql = """
        SELECT id, unit_code, blood_group, quantity_ml, expiry_date,
               status, storage_location
        FROM blood_inventory
        WHERE status IN ('Available', 'Reserved', 'Expired')
    """

    params = {}

    if blood_group != "All":
        sql += " AND blood_group = :blood_group"
        params["blood_group"] = blood_group

    sql += " ORDER BY expiry_date ASC, id ASC"

    with engine.connect() as conn:
        rows = [
            dict(r)
            for r in conn.execute(
                text(sql), params
            ).mappings().all()
        ]

    result = []

    for r in rows:
        expiry_date = _to_date(r["expiry_date"])

        if expiry_date is None:
            continue

        # Keep Python date in returned data
        r["expiry_date"] = expiry_date

        days_left = (expiry_date - today).days

        r["days_left"] = days_left
        r["bucket"] = bucket_for(days_left)

        if bucket == "All" or r["bucket"] == bucket:
            result.append(r)

    return result


def discard_unit(unit_id):
    today = date.today()

    with engine.begin() as conn:

        # SQLite does not support MySQL's FOR UPDATE
        unit = conn.execute(
            text(
                "SELECT unit_code, expiry_date, status "
                "FROM blood_inventory "
                "WHERE id = :id"
            ),
            {"id": unit_id},
        ).mappings().first()

        if unit is None:
            raise ValueError("Unit not found.")

        if unit["status"] in ("Issued", "Discarded"):
            raise ValueError(
                f"This unit is already {unit['status']}."
            )

        expiry_date = _to_date(unit["expiry_date"])

        if expiry_date >= today:
            raise ValueError(
                "Only expired units can be discarded."
            )

        # SQLite-compatible timestamp
        conn.execute(
            text(
                "UPDATE blood_inventory "
                "SET status = 'Discarded', "
                "updated_at = CURRENT_TIMESTAMP "
                "WHERE id = :id"
            ),
            {"id": unit_id},
        )

    return unit["unit_code"]

