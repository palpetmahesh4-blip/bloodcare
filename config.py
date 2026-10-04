
from pathlib import Path

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# SQLite database file
DB_PATH = BASE_DIR / "bloodcare.db"

# SQLite connection URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

