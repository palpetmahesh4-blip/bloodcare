from sqlalchemy import create_engine, text
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT DATABASE()"))
        return result.scalar()