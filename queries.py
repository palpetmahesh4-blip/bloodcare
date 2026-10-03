from datetime import date, timedelta
from sqlalchemy import text
from database import engine

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
LOW_STOCK_THRESHOLD = 2


def get_kpis():
    today = date.today()
    soon = today + timedelta(days=7)

    with engine.connect() as conn:
        total_units = conn.execute(
            text("SELECT COUNT(*) FROM blood_inventory")
        ).scalar()

        available = conn.execute(
            text("SELECT COUNT(*) FROM blood_inventory "
                 "WHERE status = 'Available' AND expiry_date >= :today"),
            {"today": today},
        ).scalar()

        expiring_soon = conn.execute(
            text("SELECT COUNT(*) FROM blood_inventory "
                 "WHERE status = 'Available' "
                 "AND expiry_date BETWEEN :today AND :soon"),
            {"today": today, "soon": soon},
        ).scalar()

        donors = conn.execute(text("SELECT COUNT(*) FROM donors")).scalar()

        pending = conn.execute(
            text("SELECT COUNT(*) FROM blood_requests WHERE status = 'Pending'")
        ).scalar()

        approved = conn.execute(
            text("SELECT COUNT(*) FROM blood_requests WHERE status = 'Approved'")
        ).scalar()

        rows = conn.execute(
            text("SELECT blood_group, COUNT(*) FROM blood_inventory "
                 "WHERE status = 'Available' AND expiry_date >= :today "
                 "GROUP BY blood_group"),
            {"today": today},
        ).all()

    stock = {group: 0 for group in BLOOD_GROUPS}
    for group, count in rows:
        stock[group] = count

    low_stock = sum(1 for count in stock.values() if count < LOW_STOCK_THRESHOLD)

    return {
        "total_units": total_units,
        "available": available,
        "low_stock": low_stock,
        "expiring_soon": expiring_soon,
        "donors": donors,
        "pending": pending,
        "approved": approved,
    }

    

def get_unread_count():
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT COUNT(*) FROM notifications WHERE is_read = 0")
        ).scalar()