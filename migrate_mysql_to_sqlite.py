import pymysql
from sqlalchemy import create_engine, text
from config import DATABASE_URL

# OLD MySQL database
mysql_conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="bloodbank_pro",
    port=3306,
    cursorclass=pymysql.cursors.DictCursor,
)

# NEW SQLite database
sqlite_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

tables = [
    "users",
    "donors",
    "blood_inventory",
    "blood_requests",
    "blood_distribution",
    "notifications",
    "activity_logs",
]

try:
    with mysql_conn.cursor() as cursor:
        with sqlite_engine.begin() as sqlite:

            for table in tables:
                print(f"Migrating: {table}")

                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()

                if not rows:
                    print(f"  → 0 rows")
                    continue

                columns = list(rows[0].keys())

                column_sql = ", ".join(f'"{c}"' for c in columns)
                value_sql = ", ".join(f":{c}" for c in columns)

                insert_sql = text(
                    f'INSERT INTO "{table}" ({column_sql}) '
                    f"VALUES ({value_sql})"
                )

                for row in rows:
                    sqlite.execute(insert_sql, row)

                print(f"  → {len(rows)} rows copied")

    print("\n✅ Migration completed successfully!")

finally:
    mysql_conn.close()