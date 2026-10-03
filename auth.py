import bcrypt
from sqlalchemy.orm import Session
from database import engine
from models import User


def authenticate(email, password):
    """Sahi email/password pe user ka dict return karta hai, warna None."""
    email = email.strip().lower()
    if not email or not password:
        return None

    with Session(engine) as session:
        user = session.query(User).filter_by(email=email, is_active=True).first()
        if user is None:
            return None

        ok = bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8"))
        if not ok:
            return None

        return {"id": user.id, "name": user.full_name, "email": user.email, "role": user.role}