
import bcrypt

from sqlalchemy import text
from database import engine


# ============================================================
# AUTHENTICATE USER
# ============================================================

def authenticate(email, password):
    """
    Authenticate an active BloodCare user.

    Returns:
        dict -> valid login
        None -> invalid email/password
    """

    # --------------------------------------------------------
    # CLEAN INPUT
    # --------------------------------------------------------

    email = str(email or "").strip().lower()
    password = str(password or "")

    if not email or not password:
        return None

    # --------------------------------------------------------
    # FIND ACTIVE USER
    # --------------------------------------------------------

    with engine.connect() as conn:

        user = conn.execute(
            text("""
                SELECT
                    id,
                    full_name,
                    email,
                    password_hash,
                    role,
                    is_active
                FROM users
                WHERE LOWER(TRIM(email)) = :email
                  AND is_active = 1
                LIMIT 1
            """),
            {
                "email": email
            }
        ).mappings().first()

    # --------------------------------------------------------
    # USER NOT FOUND
    # --------------------------------------------------------

    if user is None:
        return None

    # --------------------------------------------------------
    # CHECK PASSWORD
    # --------------------------------------------------------

    try:
        password_ok = bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        )
    except (ValueError, TypeError, AttributeError):
        return None

    if not password_ok:
        return None

    # --------------------------------------------------------
    # LOGIN SUCCESS
    # --------------------------------------------------------

    return {
        "id": user["id"],
        "name": user["full_name"],
        "email": user["email"],
        "role": user["role"],
    }

