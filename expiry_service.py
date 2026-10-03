from datetime import date
from sqlalchemy import text
from database import engine

BUCKETS = ["Expired", "Expires today", "Within 7 days", "Within 30 days", "Safe"]


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
        rows = [dict(r) for r in conn.execute(text(sql), params).mappings().all()]

    result = []
    for r in rows:
        days_left = (r["expiry_date"] - today).days
        r["days_left"] = days_left
        r["bucket"] = bucket_for(days_left)
        if bucket == "All" or r["bucket"] == bucket:
            result.append(r)

    return result

    

def discard_unit(unit_id):
    today = date.today()

    with engine.begin() as conn:
        unit = conn.execute(
            text("SELECT unit_code, expiry_date, status FROM blood_inventory "
                 "WHERE id = :id FOR UPDATE"),
            {"id": unit_id},
        ).mappings().first()

        if unit is None:
            raise ValueError("Unit not found.")
        if unit["status"] in ("Issued", "Discarded"):
            raise ValueError(f"This unit is already {unit['status']}.")
        if unit["expiry_date"] >= today:
            raise ValueError("Only expired units can be discarded.")

        conn.execute(
            text("UPDATE blood_inventory SET status = 'Discarded', updated_at = NOW() "
                 "WHERE id = :id"),
            {"id": unit_id},
        )

    return unit["unit_code"]