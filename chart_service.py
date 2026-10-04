
from datetime import date
from sqlalchemy import text
from database import engine

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


def get_stock_by_group():
    """Har blood group ke Available aur expire na hue units."""
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT blood_group, COUNT(*) "
                "FROM blood_inventory "
                "WHERE status = 'Available' AND expiry_date >= :today "
                "GROUP BY blood_group"
            ),
            {"today": date.today()},
        ).all()

    stock = {g: 0 for g in BLOOD_GROUPS}

    for group, count in rows:
        stock[group] = count

    return stock


def get_monthly_collection(months=6):
    """Pichhle `months` mahino mein har mahine ke collected units."""

    today = date.today()

    # Pichhle `months` mahino ki list (purane se naye)
    keys = []

    year = today.year
    month = today.month

    for _ in range(months):
        keys.append((year, month))

        month -= 1

        if month == 0:
            month = 12
            year -= 1

    keys.reverse()

    start = date(keys[0][0], keys[0][1], 1)

    # SQLite-compatible date extraction.
    # MySQL YEAR()/MONTH() ki jagah strftime() use kiya gaya hai.
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT "
                "CAST(strftime('%Y', collection_date) AS INTEGER) AS year, "
                "CAST(strftime('%m', collection_date) AS INTEGER) AS month, "
                "COUNT(*) "
                "FROM blood_inventory "
                "WHERE collection_date >= :start "
                "GROUP BY year, month "
                "ORDER BY year, month"
            ),
            {"start": start},
        ).all()

    counts = {(y, m): c for y, m, c in rows}

    labels = [
        date(y, m, 1).strftime("%b %Y")
        for y, m in keys
    ]

    values = [
        counts.get(k, 0)
        for k in keys
    ]

    return labels, values


def get_request_status_counts():
    """Har status ki kitni requests hain."""

    statuses = [
        "Pending",
        "Approved",
        "Fulfilled",
        "Rejected",
    ]

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT status, COUNT(*) "
                "FROM blood_requests "
                "GROUP BY status"
            )
        ).all()

    counts = {s: 0 for s in statuses}

    for status, count in rows:
        if status in counts:
            counts[status] = count

    return counts


def get_expiry_overview():
    """Stock mein jo units hain, unke expiry buckets ka count."""

    from expiry_service import get_expiry_units, BUCKETS

    units = get_expiry_units()

    counts = {b: 0 for b in BUCKETS}

    for u in units:
        counts[u["bucket"]] += 1

    return counts



