from sqlalchemy import text
from database import engine
from user_service import change_password

with engine.connect() as conn:
    admin_id = conn.execute(
        text("SELECT id FROM users WHERE email = 'admin@bloodbank.in'")
    ).scalar()

try:
    change_password(admin_id, "this-is-wrong", "SomeNewPass123")
except ValueError as e:
    print("Error:", e)