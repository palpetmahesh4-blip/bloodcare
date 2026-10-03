from sqlalchemy import text
from database import engine

tables = [
    "users", "donors", "blood_inventory", "blood_requests",
    "blood_distribution", "notifications", "activity_logs",
]

with engine.connect() as conn:
    for t in tables:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        print(f"{t}: {count}")