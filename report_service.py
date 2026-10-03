import pandas as pd
from sqlalchemy import text
from database import engine


def _run(sql, params):
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])


def inventory_report(date_from, date_to, blood_group="All"):
    sql = """
        SELECT b.unit_code AS `Unit ID`, d.full_name AS `Donor`,
               b.blood_group AS `Group`, b.quantity_ml AS `Qty (ml)`,
               b.collection_date AS `Collected`, b.expiry_date AS `Expiry`,
               b.status AS `Status`, b.storage_location AS `Location`
        FROM blood_inventory b
        JOIN donors d ON d.id = b.donor_id
        WHERE b.collection_date BETWEEN :date_from AND :date_to
    """
    params = {"date_from": date_from, "date_to": date_to}

    if blood_group != "All":
        sql += " AND b.blood_group = :blood_group"
        params["blood_group"] = blood_group

    sql += " ORDER BY b.collection_date DESC, b.id DESC"
    return _run(sql, params)

    

def donor_report(date_from, date_to, blood_group="All"):
    sql = """
        SELECT d.donor_code AS `Donor ID`, d.full_name AS `Name`,
               d.gender AS `Gender`, d.blood_group AS `Group`,
               d.phone AS `Phone`, d.city AS `City`,
               d.last_donation_date AS `Last donation`,
               COUNT(b.id) AS `Units donated`,
               CASE WHEN d.is_eligible = 1 THEN 'Eligible' ELSE 'Not eligible' END AS `Eligibility`
        FROM donors d
        LEFT JOIN blood_inventory b ON b.donor_id = d.id
        WHERE DATE(d.created_at) BETWEEN :date_from AND :date_to
    """
    params = {"date_from": date_from, "date_to": date_to}

    if blood_group != "All":
        sql += " AND d.blood_group = :blood_group"
        params["blood_group"] = blood_group

    sql += " GROUP BY d.id ORDER BY d.full_name ASC"
    return _run(sql, params)


def request_report(date_from, date_to, blood_group="All"):
    sql = """
        SELECT r.request_code AS `Request ID`, r.patient_name AS `Patient`,
               r.patient_age AS `Age`, r.hospital_name AS `Hospital`,
               r.blood_group AS `Group`, r.units_required AS `Units`,
               r.urgency AS `Urgency`, r.status AS `Status`,
               r.request_date AS `Date`
        FROM blood_requests r
        WHERE r.request_date BETWEEN :date_from AND :date_to
    """
    params = {"date_from": date_from, "date_to": date_to}

    if blood_group != "All":
        sql += " AND r.blood_group = :blood_group"
        params["blood_group"] = blood_group

    sql += " ORDER BY r.request_date DESC, r.id DESC"
    return _run(sql, params)


def distribution_report(date_from, date_to, blood_group="All"):
    sql = """
        SELECT d.distribution_code AS `Dist ID`, r.request_code AS `Request`,
               i.unit_code AS `Unit`, i.blood_group AS `Group`,
               d.quantity_ml AS `Qty (ml)`, d.hospital_name AS `Hospital`,
               d.patient_name AS `Patient`, d.issue_date AS `Issue date`,
               u.full_name AS `Issued by`, d.status AS `Status`
        FROM blood_distribution d
        JOIN blood_requests r ON r.id = d.request_id
        JOIN blood_inventory i ON i.id = d.inventory_id
        JOIN users u ON u.id = d.issued_by
        WHERE d.issue_date BETWEEN :date_from AND :date_to
    """
    params = {"date_from": date_from, "date_to": date_to}

    if blood_group != "All":
        sql += " AND i.blood_group = :blood_group"
        params["blood_group"] = blood_group

    sql += " ORDER BY d.issue_date DESC, d.id DESC"
    return _run(sql, params)


def expiry_report(date_from, date_to, blood_group="All"):
    sql = """
        SELECT b.unit_code AS `Unit ID`, b.blood_group AS `Group`,
               b.quantity_ml AS `Qty (ml)`, b.expiry_date AS `Expiry date`,
               DATEDIFF(b.expiry_date, CURDATE()) AS `Days left`,
               b.status AS `Status`, b.storage_location AS `Location`
        FROM blood_inventory b
        WHERE b.expiry_date BETWEEN :date_from AND :date_to
    """
    params = {"date_from": date_from, "date_to": date_to}

    if blood_group != "All":
        sql += " AND b.blood_group = :blood_group"
        params["blood_group"] = blood_group

    sql += " ORDER BY b.expiry_date ASC, b.id ASC"
    return _run(sql, params)