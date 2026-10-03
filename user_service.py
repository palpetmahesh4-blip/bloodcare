import bcrypt
from sqlalchemy import text
from database import engine


def change_password(user_id, current_password, new_password):
    if len(new_password) < 8:
        raise ValueError("New password must be at least 8 characters.")
    if new_password == current_password:
        raise ValueError("New password must be different from the current one.")

    with engine.begin() as conn:
        stored = conn.execute(
            text("SELECT password_hash FROM users WHERE id = :id"),
            {"id": user_id},
        ).scalar()

        if stored is None:
            raise ValueError("User not found.")

        ok = bcrypt.checkpw(current_password.encode("utf-8"), stored.encode("utf-8"))
        if not ok:
            raise ValueError("Current password is incorrect.")

        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn.execute(
            text("UPDATE users SET password_hash = :h, updated_at = NOW() WHERE id = :id"),
            {"h": new_hash, "id": user_id},
        )

        

def list_users():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, full_name, email, role, is_active, created_at "
                 "FROM users ORDER BY is_active DESC, role ASC, full_name ASC")
        ).mappings().all()
    return [dict(r) for r in rows]


def create_user(full_name, email, password, role):
    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name:
        raise ValueError("Please enter the full name.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Please enter a valid email address.")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if role not in ("admin", "staff"):
        raise ValueError("Role must be admin or staff.")

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT COUNT(*) FROM users WHERE email = :email"),
            {"email": email},
        ).scalar()
        if exists:
            raise ValueError("A user with this email already exists.")

        conn.execute(
            text("""
                INSERT INTO users
                    (full_name, email, password_hash, role, is_active, created_at, updated_at)
                VALUES
                    (:full_name, :email, :password_hash, :role, 1, NOW(), NOW())
            """),
            {
                "full_name": full_name,
                "email": email,
                "password_hash": password_hash,
                "role": role,
            },
        )
    return email


def set_user_active(user_id, active, acting_user_id):
    if user_id == acting_user_id and not active:
        raise ValueError("You cannot deactivate your own account.")

    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET is_active = :active, updated_at = NOW() WHERE id = :id"),
            {"active": 1 if active else 0, "id": user_id},
        )