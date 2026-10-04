
from datetime import date

from sqlalchemy import text
from database import engine

with engine.begin() as conn:
    res = conn.execute(
        text("""
            UPDATE donors
            SET
                last_donation_date = (
                    SELECT MAX(collection_date)
                    FROM blood_inventory
                    WHERE blood_inventory.donor_id = donors.id
                ),
                is_eligible = CASE
                    WHEN (
                        SELECT MAX(collection_date)
                        FROM blood_inventory
                        WHERE blood_inventory.donor_id = donors.id
                    ) IS NOT NULL
                    AND julianday(:today) - julianday(
                        (
                            SELECT MAX(collection_date)
                            FROM blood_inventory
                            WHERE blood_inventory.donor_id = donors.id
                        )
                    ) >= 90
                    THEN 1
                    ELSE 0
                END,
                updated_at = CURRENT_TIMESTAMP
            WHERE donor_code <= 'D012'
              AND EXISTS (
                  SELECT 1
                  FROM blood_inventory
                  WHERE blood_inventory.donor_id = donors.id
              )
        """),
        {"today": date.today().isoformat()},
    )

    print("Donors updated:", res.rowcount)

