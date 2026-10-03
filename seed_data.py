from datetime import date, timedelta
import bcrypt
from sqlalchemy.orm import Session
from database import engine
from models import User, Donor, BloodInventory, BloodRequest


def hash_password(plain):
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_users(session, password):
    users = [
        ("Dr. Rajesh Kulkarni", "admin@bloodbank.in", "admin"),
        ("Priya Deshmukh", "staff@bloodbank.in", "staff"),
    ]
    for full_name, email, role in users:
        exists = session.query(User).filter_by(email=email).first()
        if exists:
            print(f"Skipped (already exists): {email}")
            continue
        session.add(User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role=role,
        ))
        print(f"Added user: {email}")
    session.commit()


def seed_donors(session):
    donors = [
        ("D001", "Amit Patil", "Male", date(1994, 3, 12), "B+", "9820010001", "Pune", date(2026, 5, 10), True),
        ("D002", "Sneha Joshi", "Female", date(1998, 7, 25), "O+", "9820010002", "Mumbai", date(2026, 4, 18), True),
        ("D003", "Rohan Mehta", "Male", date(1990, 11, 2), "A+", "9820010003", "Thane", date(2026, 9, 10), False),
        ("D004", "Kavita Sharma", "Female", date(1995, 1, 19), "AB+", "9820010004", "Nagpur", date(2026, 3, 5), True),
        ("D005", "Vikram Singh", "Male", date(1988, 9, 30), "O-", "9820010005", "Delhi", date(2026, 6, 15), True),
        ("D006", "Pooja Nair", "Female", date(1999, 5, 8), "A-", "9820010006", "Kochi", date(2026, 8, 20), False),
        ("D007", "Suresh Iyer", "Male", date(1985, 12, 14), "B-", "9820010007", "Chennai", date(2026, 2, 11), True),
        ("D008", "Ananya Reddy", "Female", date(1997, 4, 3), "AB-", "9820010008", "Hyderabad", None, True),
        ("D009", "Manoj Gupta", "Male", date(1992, 8, 21), "O+", "9820010009", "Lucknow", date(2026, 5, 28), True),
        ("D010", "Neha Kulkarni", "Female", date(2000, 2, 27), "B+", "9820010010", "Nashik", date(2026, 9, 1), False),
        ("D011", "Arjun Verma", "Male", date(1991, 6, 16), "A+", "9820010011", "Jaipur", date(2026, 4, 2), True),
        ("D012", "Divya Menon", "Female", date(1996, 10, 9), "O+", "9820010012", "Bengaluru", date(2026, 1, 22), True),
    ]
    for code, name, gender, dob, group, phone, city, last_don, eligible in donors:
        exists = session.query(Donor).filter_by(donor_code=code).first()
        if exists:
            print(f"Skipped (already exists): {code}")
            continue
        session.add(Donor(
            donor_code=code,
            full_name=name,
            gender=gender,
            date_of_birth=dob,
            blood_group=group,
            phone=phone,
            city=city,
            last_donation_date=last_don,
            is_eligible=eligible,
        ))
        print(f"Added donor: {code} {name}")
    session.commit()


def seed_inventory(session):
    today = date.today()
    # (unit_code, donor_code, blood_group, quantity_ml, days_ago_collected, shelf_life_days, status, location)
    units = [
        ("U001", "D001", "B+", 450, 10, 42, "Available", "Fridge A1"),
        ("U002", "D002", "O+", 450, 5, 42, "Available", "Fridge A2"),
        ("U003", "D009", "O+", 450, 12, 42, "Available", "Fridge A2"),
        ("U004", "D005", "O-", 350, 8, 42, "Available", "Fridge B1"),
        ("U005", "D004", "AB+", 450, 20, 42, "Available", "Fridge B2"),
        ("U006", "D011", "A+", 450, 3, 42, "Reserved", "Fridge A3"),
        ("U007", "D007", "B-", 450, 15, 42, "Available", "Fridge B1"),
        ("U008", "D012", "O+", 450, 39, 42, "Available", "Fridge A2"),
        ("U009", "D003", "A+", 450, 36, 42, "Available", "Fridge A3"),
        ("U010", "D010", "B+", 450, 42, 42, "Available", "Fridge A1"),
        ("U011", "D006", "A-", 450, 50, 42, "Expired", "Fridge B3"),
        ("U012", "D001", "B+", 450, 30, 42, "Issued", "Fridge A1"),
        ("U013", "D002", "O+", 450, 25, 42, "Issued", "Fridge A2"),
        ("U014", "D008", "AB-", 450, 18, 42, "Available", "Fridge B2"),
        ("U015", "D005", "O-", 450, 55, 42, "Discarded", "Fridge B3"),
        ("U016", "D009", "O+", 350, 2, 42, "Available", "Fridge A2"),
    ]
    for unit_code, donor_code, group, qty, days_ago, shelf, status, location in units:
        exists = session.query(BloodInventory).filter_by(unit_code=unit_code).first()
        if exists:
            print(f"Skipped (already exists): {unit_code}")
            continue
        donor = session.query(Donor).filter_by(donor_code=donor_code).first()
        if donor is None:
            print(f"Donor {donor_code} not found, skipping {unit_code}")
            continue
        collected = today - timedelta(days=days_ago)
        session.add(BloodInventory(
            unit_code=unit_code,
            donor_id=donor.id,
            blood_group=group,
            quantity_ml=qty,
            collection_date=collected,
            expiry_date=collected + timedelta(days=shelf),
            status=status,
            storage_location=location,
        ))
        print(f"Added unit: {unit_code} ({group}, {status})")
    session.commit()


def seed_requests(session):
    today = date.today()
    staff = session.query(User).filter_by(email="staff@bloodbank.in").first()
    if staff is None:
        print("Staff user not found, skipping requests.")
        return
    # (request_code, patient_name, age, hospital, blood_group, units, urgency, status, days_ago)
    requests = [
        ("R001", "Ramesh Kadam", 54, "Ruby Hall Clinic, Pune", "B+", 1, "Normal", "Fulfilled", 12),
        ("R002", "Sunita Bhosale", 38, "Lilavati Hospital, Mumbai", "O+", 1, "Urgent", "Fulfilled", 9),
        ("R003", "Mohan Rao", 61, "Apollo Hospital, Hyderabad", "AB-", 2, "Urgent", "Approved", 2),
        ("R004", "Fatima Sheikh", 29, "KEM Hospital, Mumbai", "O-", 3, "Emergency", "Pending", 0),
        ("R005", "Deepak Yadav", 45, "AIIMS, Delhi", "A+", 2, "Normal", "Pending", 1),
        ("R006", "Lakshmi Iyer", 67, "Fortis Hospital, Chennai", "B-", 1, "Normal", "Rejected", 6),
        ("R007", "Sanjay Pawar", 33, "Sahyadri Hospital, Pune", "O+", 2, "Emergency", "Pending", 0),
        ("R008", "Meena Kulkarni", 50, "Jehangir Hospital, Pune", "B+", 1, "Normal", "Approved", 3),
        ("R009", "Imran Khan", 41, "Medanta, Gurugram", "A-", 1, "Urgent", "Pending", 1),
        ("R010", "Rekha Menon", 58, "Aster Medcity, Kochi", "AB+", 1, "Normal", "Fulfilled", 15),
    ]
    for code, patient, age, hospital, group, units, urgency, status, days_ago in requests:
        exists = session.query(BloodRequest).filter_by(request_code=code).first()
        if exists:
            print(f"Skipped (already exists): {code}")
            continue
        session.add(BloodRequest(
            request_code=code,
            patient_name=patient,
            patient_age=age,
            hospital_name=hospital,
            blood_group=group,
            units_required=units,
            urgency=urgency,
            status=status,
            requested_by=staff.id,
            request_date=today - timedelta(days=days_ago),
        ))
        print(f"Added request: {code} ({group}, {urgency}, {status})")
    session.commit()


if __name__ == "__main__":
    with Session(engine) as session:
        if session.query(User).count() == 0:
            demo_password = input("Demo login ke liye ek password chuno (yaad rakhna): ")
            seed_users(session, demo_password)
        else:
            print("Users already exist, skipping users.")
        seed_donors(session)
        seed_inventory(session)
        seed_requests(session)
    print("Seeding done!") 	