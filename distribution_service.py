from sqlalchemy import text
from database import engine


def get_distributions(search="", blood_group="All"):
    sql = """
        SELECT
            d.id, d.distribution_code, r.request_code, i.unit_code,
            i.blood_group, d.quantity_ml, d.hospital_name, d.patient_name,
            d.issue_date, u.full_name AS issued_by_name, d.status
        FROM blood_distribution d
        JOIN blood_requests r ON r.id = d.request_id
        JOIN blood_inventory i ON i.id = d.inventory_id
        JOIN users u ON u.id = d.issued_by
        WHERE 1 = 1
    """
    params = {}

    if search:
        sql += (" AND (d.distribution_code LIKE :search OR i.unit_code LIKE :search "
                "OR d.patient_name LIKE :search OR d.hospital_name LIKE :search "
                "OR r.request_code LIKE :search)")
        params["search"] = f"%{search}%"

    if blood_group != "All":
        sql += " AND i.blood_group = :blood_group"
        params["blood_group"] = blood_group

    sql += " ORDER BY d.issue_date DESC, d.id DESC"

    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()

    return [dict(r) for r in rows]