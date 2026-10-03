from sqlalchemy import text
from database import engine


def get_requests(search="", blood_group="All", status="All", urgency="All"):
    sql = """
        SELECT
            r.id, r.request_code, r.patient_name, r.patient_age,
            r.hospital_name, r.blood_group, r.units_required,
            r.urgency, r.status, r.request_date,
            u.full_name AS requested_by_name
        FROM blood_requests r
        LEFT JOIN users u ON u.id = r.requested_by
        WHERE 1 = 1
    """
    params = {}

    if search:
        sql += (" AND (r.request_code LIKE :search OR r.patient_name LIKE :search "
                "OR r.hospital_name LIKE :search)")
        params["search"] = f"%{search}%"

    if blood_group != "All":
        sql += " AND r.blood_group = :blood_group"
        params["blood_group"] = blood_group

    if status != "All":
        sql += " AND r.status = :status"
        params["status"] = status

    if urgency != "All":
        sql += " AND r.urgency = :urgency"
        params["urgency"] = urgency

    sql += (" ORDER BY FIELD(r.urgency, 'Emergency', 'Urgent', 'Normal'), "
            "r.request_date DESC, r.id DESC")

    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()

    return [dict(r) for r in rows]

    

def add_request(patient_name, patient_age, hospital_name, blood_group,
                units_required, urgency, requested_by):
    from datetime import date

    if not patient_name.strip():
        raise ValueError("Please enter the patient's name.")
    if not hospital_name.strip():
        raise ValueError("Please enter the hospital name.")
    if units_required < 1 or units_required > 10:
        raise ValueError("Units required must be between 1 and 10.")
    if patient_age is not None and (patient_age < 0 or patient_age > 120):
        raise ValueError("Please enter a valid patient age.")

    with engine.begin() as conn:
        last = conn.execute(
            text("SELECT MAX(CAST(SUBSTRING(request_code, 2) AS UNSIGNED)) FROM blood_requests")
        ).scalar() or 0
        request_code = f"R{last + 1:03d}"

        conn.execute(
            text("""
                INSERT INTO blood_requests
                    (request_code, patient_name, patient_age, hospital_name, blood_group,
                     units_required, urgency, status, requested_by, request_date,
                     created_at, updated_at)
                VALUES
                    (:request_code, :patient_name, :patient_age, :hospital_name, :blood_group,
                     :units_required, :urgency, 'Pending', :requested_by, :request_date,
                     NOW(), NOW())
            """),
            {
                "request_code": request_code,
                "patient_name": patient_name.strip(),
                "patient_age": patient_age,
                "hospital_name": hospital_name.strip(),
                "blood_group": blood_group,
                "units_required": units_required,
                "urgency": urgency,
                "requested_by": requested_by,
                "request_date": date.today(),
            },
        )
    return request_code


    

def _change_pending_status(request_id, new_status):
    with engine.begin() as conn:
        current = conn.execute(
            text("SELECT status FROM blood_requests WHERE id = :id"),
            {"id": request_id},
        ).scalar()

        if current is None:
            raise ValueError("Request not found.")
        if current != "Pending":
            raise ValueError(f"Only Pending requests can be changed. This one is {current}.")

        conn.execute(
            text("UPDATE blood_requests SET status = :status, updated_at = NOW() WHERE id = :id"),
            {"status": new_status, "id": request_id},
        )


def approve_request(request_id):
    _change_pending_status(request_id, "Approved")


def reject_request(request_id):
    _change_pending_status(request_id, "Rejected")

    

def fulfill_request(request_id, issued_by):
    from datetime import date

    today = date.today()

    with engine.begin() as conn:
        req = conn.execute(
            text("""
                SELECT id, request_code, patient_name, hospital_name,
                       blood_group, units_required, status
                FROM blood_requests
                WHERE id = :id
                FOR UPDATE
            """),
            {"id": request_id},
        ).mappings().first()

        if req is None:
            raise ValueError("Request not found.")
        if req["status"] != "Approved":
            raise ValueError(
                f"Only Approved requests can be fulfilled. This one is {req['status']}."
            )

        needed = int(req["units_required"])
        units = conn.execute(
            text("""
                SELECT id, unit_code, quantity_ml
                FROM blood_inventory
                WHERE blood_group = :group
                  AND status = 'Available'
                  AND expiry_date >= :today
                ORDER BY expiry_date ASC, id ASC
                LIMIT :n
                FOR UPDATE
            """),
            {"group": req["blood_group"], "today": today, "n": needed},
        ).mappings().all()

        if len(units) < needed:
            raise ValueError(
                f"Not enough stock: {needed} unit(s) of {req['blood_group']} needed, "
                f"only {len(units)} available."
            )

        last = conn.execute(
            text("SELECT MAX(CAST(SUBSTRING(distribution_code, 4) AS UNSIGNED)) "
                 "FROM blood_distribution")
        ).scalar() or 0

        issued_codes = []
        for i, unit in enumerate(units, start=1):
            conn.execute(
                text("""
                    INSERT INTO blood_distribution
                        (distribution_code, request_id, inventory_id, hospital_name,
                         patient_name, quantity_ml, issue_date, issued_by, status,
                         created_at, updated_at)
                    VALUES
                        (:code, :request_id, :inventory_id, :hospital, :patient,
                         :qty, :issue_date, :issued_by, 'Completed', NOW(), NOW())
                """),
                {
                    "code": f"DIS{last + i:03d}",
                    "request_id": req["id"],
                    "inventory_id": unit["id"],
                    "hospital": req["hospital_name"],
                    "patient": req["patient_name"],
                    "qty": unit["quantity_ml"],
                    "issue_date": today,
                    "issued_by": issued_by,
                },
            )
            conn.execute(
                text("UPDATE blood_inventory SET status = 'Issued', updated_at = NOW() "
                     "WHERE id = :id"),
                {"id": unit["id"]},
            )
            issued_codes.append(unit["unit_code"])

        conn.execute(
            text("UPDATE blood_requests SET status = 'Fulfilled', updated_at = NOW() "
                 "WHERE id = :id"),
            {"id": req["id"]},
        )

    return issued_codes