from sqlalchemy import text

from database import engine

DONOR_COLUMNS = "d.donor_code, d.full_name, d.blood_group, d.phone, d.city"
DONOR_FROM = (
    "FROM donors d WHERE d.full_name LIKE :q OR d.donor_code LIKE :q "
    "OR d.phone LIKE :q OR d.city LIKE :q OR d.blood_group LIKE :q"
)

UNIT_COLUMNS = ("b.unit_code, d.full_name AS donor_name, b.blood_group, "
                "b.quantity_ml, b.expiry_date, b.status, b.storage_location")
UNIT_FROM = (
    "FROM blood_inventory b JOIN donors d ON d.id = b.donor_id "
    "WHERE b.unit_code LIKE :q OR d.full_name LIKE :q OR b.blood_group LIKE :q "
    "OR b.status LIKE :q OR b.storage_location LIKE :q"
)

REQUEST_COLUMNS = ("r.request_code, r.patient_name, r.hospital_name, r.blood_group, "
                   "r.units_required, r.urgency, r.status")
REQUEST_FROM = (
    "FROM blood_requests r WHERE r.request_code LIKE :q OR r.patient_name LIKE :q "
    "OR r.hospital_name LIKE :q OR r.blood_group LIKE :q OR r.status LIKE :q"
)


def _run(conn, columns, from_where, order, params, limit):
    total = conn.execute(text(f"SELECT COUNT(*) {from_where}"), params).scalar()
    rows = conn.execute(
        text(f"SELECT {columns} {from_where} ORDER BY {order} LIMIT {int(limit)}"),
        params,
    ).mappings().all()
    return {"total": total, "rows": [dict(r) for r in rows]}


def global_search(query, limit=10):
    """Teeno jagah dhundhta hai. Bahut chhota query ho to None lautata hai."""
    q = (query or "").strip()
    if len(q) < 2:
        return None

    params = {"q": f"%{q}%"}
    with engine.connect() as conn:
        return {
            "donors": _run(conn, DONOR_COLUMNS, DONOR_FROM, "d.full_name", params, limit),
            "units": _run(conn, UNIT_COLUMNS, UNIT_FROM, "b.expiry_date", params, limit),
            "requests": _run(conn, REQUEST_COLUMNS, REQUEST_FROM,
                             "r.request_date DESC, r.id DESC", params, limit),
        }