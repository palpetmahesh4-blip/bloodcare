
from pathlib import Path
import shutil
import tempfile

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# Original database shipped with the project
SOURCE_DB_PATH = BASE_DIR / "bloodcare.db"

# Streamlit Cloud gives /tmp as a writable location.
# Local development will continue using the project database.
if Path("/mount/src").exists():
    DB_PATH = Path(tempfile.gettempdir()) / "bloodcare.db"

    # Copy the original database only if a writable copy does not exist.
    if SOURCE_DB_PATH.exists() and not DB_PATH.exists():
        shutil.copy2(SOURCE_DB_PATH, DB_PATH)
else:
    DB_PATH = SOURCE_DB_PATH

# SQLite connection URL
DATABASE_URL = f"sqlite:///{DB_PATH}"

