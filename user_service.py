
import bcrypt

from sqlalchemy import text
from database import engine


# ============================================================
# CHANGE PASSWORD
# ============================================================

def change_password(
    user_id,
    current_password,
    new_password
):
    if len(new_password) < 8:
        raise ValueError(
            "New password must be at least 8 characters."
        )

    if new_password == current_password:
        raise ValueError(
            "New password must be different from the current one."
        )

    with engine.begin() as conn:

        stored = conn.execute(
            text("""
                SELECT password_hash
                FROM users
                WHERE id = :id
            """),
            {
                "id": user_id
            }
        ).scalar()

        if stored is None:
            raise ValueError(
                "User not found."
            )

        ok = bcrypt.checkpw(
            current_password.encode("utf-8"),
            stored.encode("utf-8")
        )

        if not ok:
            raise ValueError(
                "Current password is incorrect."
            )

        new_hash = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        conn.execute(
            text("""
                UPDATE users
                SET
                    password_hash = :password_hash,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """),
            {
                "password_hash": new_hash,
                "id": user_id
            }
        )


# ============================================================
# LIST USERS
# ============================================================

def list_users():

    with engine.connect() as conn:

        rows = conn.execute(
            text("""
                SELECT
                    id,
                    full_name,
                    email,
                    role,
                    is_active,
                    created_at
                FROM users
                ORDER BY
                    is_active DESC,
                    role ASC,
                    full_name ASC
            """)
        ).mappings().all()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# CREATE USER
# ============================================================

def create_user(
    full_name,
    email,
    password,
    role="staff"
):
    """
    Create a new BloodCare user.

    New accounts created from the registration page
    are normally Staff accounts.
    """

    # --------------------------------------------------------
    # CLEAN INPUT
    # --------------------------------------------------------

    full_name = str(full_name or "").strip()
    email = str(email or "").strip().lower()
    password = str(password or "")

    # --------------------------------------------------------
    # VALIDATE NAME
    # --------------------------------------------------------

    if not full_name:
        raise ValueError(
            "Please enter the full name."
        )

    if len(full_name) < 2:
        raise ValueError(
            "Please enter a valid full name."
        )

    # --------------------------------------------------------
    # VALIDATE EMAIL
    # --------------------------------------------------------

    if (
        "@" not in email
        or "." not in email.split("@")[-1]
        or email.startswith("@")
        or email.endswith("@")
    ):
        raise ValueError(
            "Please enter a valid email address."
        )

    # --------------------------------------------------------
    # VALIDATE PASSWORD
    # --------------------------------------------------------

    if len(password) < 8:
        raise ValueError(
            "Password must be at least 8 characters."
        )

    # --------------------------------------------------------
    # VALIDATE ROLE
    # --------------------------------------------------------

    if role not in (
        "admin",
        "staff"
    ):
        raise ValueError(
            "Role must be admin or staff."
        )

    # --------------------------------------------------------
    # CHECK EXISTING USER
    # --------------------------------------------------------

    with engine.begin() as conn:

        existing_user = conn.execute(
            text("""
                SELECT
                    id,
                    email,
                    is_active
                FROM users
                WHERE LOWER(TRIM(email)) = :email
                LIMIT 1
            """),
            {
                "email": email
            }
        ).mappings().first()

        if existing_user is not None:

            if existing_user["is_active"]:
                raise ValueError(
                    "A user with this email already exists."
                )

            raise ValueError(
                "An account with this email already exists "
                "but is currently inactive. Please contact "
                "the administrator."
            )

        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # ----------------------------------------------------
        # INSERT NEW USER
        # ----------------------------------------------------

        conn.execute(
            text("""
                INSERT INTO users
                (
                    full_name,
                    email,
                    password_hash,
                    role,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES
                (
                    :full_name,
                    :email,
                    :password_hash,
                    :role,
                    1,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP
                )
            """),
            {
                "full_name": full_name,
                "email": email,
                "password_hash": password_hash,
                "role": role
            }
        )

    return email


# ============================================================
# ACTIVATE / DEACTIVATE USER
# ============================================================

def set_user_active(
    user_id,
    active,
    acting_user_id
):

    if (
        user_id == acting_user_id
        and not active
    ):
        raise ValueError(
            "You cannot deactivate your own account."
        )

    with engine.begin() as conn:

        result = conn.execute(
            text("""
                UPDATE users
                SET
                    is_active = :active,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """),
            {
                "active": 1 if active else 0,
                "id": user_id
            }
        )

        if result.rowcount == 0:
            raise ValueError(
                "User not found."
            )

