
from sqlalchemy import create_engine, text

from config import DATABASE_URL


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={
        "check_same_thread": False
    }
)


# ============================================================
# DATABASE CONNECTION TEST
# ============================================================

def test_connection():

    with engine.connect() as conn:

        # SQLite-compatible connection test
        result = conn.execute(
            text("SELECT 1")
        )

        return result.scalar()

