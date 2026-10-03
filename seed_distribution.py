from datetime import date, timedelta
from sqlalchemy.orm import Session
from database import engine
from models import User, BloodRequest, BloodInventory, BloodDistribution

# (distribution_code, request_code, unit_code)
links = [
    ("DIS001", "R001", "U012"),
    ("DIS002", "R002", "U013"),
    ("DIS003", "R010", "U005"),
]

with Session(engine) as session:
    staff = session.query(User).filter_by(email="staff@bloodbank.in").first()

    for dis_code, req_code, unit_code in links:
        if session.query(BloodDistribution).filter_by(distribution_code=dis_code).first():
            print(f"Skipped (already exists): {dis_code}")
            continue

        req = session.query(BloodRequest).filter_by(request_code=req_code).first()
        unit = session.query(BloodInventory).filter_by(unit_code=unit_code).first()
        if req is None or unit is None:
            print(f"Missing data for {dis_code}, skipping")
            continue

        unit.status = "Issued"
        session.add(BloodDistribution(
            distribution_code=dis_code,
            request_id=req.id,
            inventory_id=unit.id,
            hospital_name=req.hospital_name,
            patient_name=req.patient_name,
            quantity_ml=unit.quantity_ml,
            issue_date=req.request_date + timedelta(days=1),
            issued_by=staff.id,
            status="Completed",
        ))
        print(f"Added distribution: {dis_code} ({req_code} -> {unit_code})")

    session.commit()

print("Done!")