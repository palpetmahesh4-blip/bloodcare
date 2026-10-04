import random
from collections import Counter
from datetime import date, datetime, time, timedelta

from sqlalchemy import text

from database import engine

random.seed(7)

NEW_DONORS = 320
NEW_UNITS = 500
SHELF_LIFE_DAYS = 42
TODAY = date.today()

MALE_FIRST = ["Aarav", "Rohan", "Amit", "Vikram", "Suresh", "Rahul", "Manoj", "Sanjay",
              "Deepak", "Arjun", "Nikhil", "Prasad", "Rajesh", "Karan", "Siddharth",
              "Imran", "Faisal", "Gurpreet", "Harsh", "Yash", "Omkar", "Tejas", "Ganesh",
              "Kiran", "Mahesh"]
FEMALE_FIRST = ["Sneha", "Priya", "Kavita", "Pooja", "Ananya", "Neha", "Divya", "Meera",
                "Sunita", "Rekha", "Anjali", "Shruti", "Swati", "Aditi", "Fatima",
                "Simran", "Isha", "Pallavi", "Madhuri", "Rutuja", "Komal", "Nisha",
                "Radhika", "Jyoti", "Sakshi"]
LAST = ["Patil", "Joshi", "Sharma", "Mehta", "Singh", "Nair", "Iyer", "Reddy", "Gupta",
        "Kulkarni", "Deshmukh", "Verma", "Menon", "Shaikh", "Khan", "Pawar", "Jadhav",
        "Shinde", "More", "Kadam", "Bhosale", "Chavan", "Desai", "Rao", "Yadav",
        "Gaikwad", "Thakur", "Kapoor", "Bose", "Das"]
CITIES = ["Mumbai", "Pune", "Thane", "Nashik", "Nagpur", "Navi Mumbai", "Kolhapur",
          "Aurangabad", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Ahmedabad",
          "Jaipur", "Lucknow", "Kochi", "Indore", "Bhopal"]

# India mein blood groups ka lagbhag asli ratio
GROUPS = ["O+", "B+", "A+", "AB+", "O-", "B-", "A-", "AB-"]
WEIGHTS = [33, 30, 21, 7, 3, 2.5, 2.5, 1]
LOCATIONS = ["Fridge A1", "Fridge A2", "Fridge A3", "Fridge B1",
             "Fridge B2", "Fridge B3", "Fridge C1", "Fridge C2"]


def make_donors(last_number):
    donors = []
    for i in range(NEW_DONORS):
        gender = random.choices(["Male", "Female"], [55, 45])[0]
        first = random.choice(MALE_FIRST if gender == "Male" else FEMALE_FIRST)
        last = random.choice(LAST)
        n = last_number + i + 1
        email = f"{first}.{last}{n}@example.com".lower() if random.random() < 0.6 else None
        donors.append({
            "donor_code": f"D{n:03d}",
            "full_name": f"{first} {last}",
            "gender": gender,
            "date_of_birth": TODAY - timedelta(days=random.randint(19 * 365, 58 * 365)),
            "blood_group": random.choices(GROUPS, WEIGHTS)[0],
            "phone": f"98200{20000 + i}",
            "email": email,
            "city": random.choice(CITIES),
        })
    return donors


def pick_days_ago():
    d = random.randint(0, 179)
    return d + 1 if d >= 42 else d   # 42 din wala case skip (aaj expire hone wala)


def pick_status(days_ago):
    r = random.random()
    if days_ago <= 41:
        if r < 0.80:
            return "Available"
        if r < 0.86:
            return "Reserved"
        return "Issued"
    if r < 0.80:
        return "Issued"
    if r < 0.92:
        return "Discarded"
    return "Expired"


with engine.begin() as conn:
    existing = conn.execute(text("SELECT COUNT(*) FROM donors")).scalar()
    if existing > 100:
        print("Bulk data already exists. Stopping.")
        raise SystemExit

    last_donor = conn.execute(
        text("SELECT MAX(CAST(SUBSTRING(donor_code, 2) AS UNSIGNED)) FROM donors")
    ).scalar() or 0
    last_unit = conn.execute(
        text("SELECT MAX(CAST(SUBSTRING(unit_code, 2) AS UNSIGNED)) FROM blood_inventory")
    ).scalar() or 0

    # 1. Donors daalo
    conn.execute(
        text("""
            INSERT INTO donors
                (donor_code, full_name, gender, date_of_birth, blood_group, phone,
                 email, city, last_donation_date, is_eligible, created_at, updated_at)
           VALUES
    (:donor_code, :full_name, :gender, :date_of_birth, :blood_group, :phone,
     :email, :city, NULL, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """),
        make_donors(last_donor),
    )

    donor_rows = [
        dict(r) for r in conn.execute(
            text("SELECT id, donor_code, blood_group FROM donors "
                 "WHERE CAST(SUBSTRING(donor_code, 2) AS UNSIGNED) > :n"),
            {"n": last_donor},
        ).mappings().all()
    ]

    # 2. Units banao (ek donor ki 2 donations ke beech kam se kam 90 din)
    donor_dates = {d["id"]: [] for d in donor_rows}
    units = []
    for _ in range(NEW_UNITS):
        days_ago = pick_days_ago()
        collected = TODAY - timedelta(days=days_ago)

        donor = None
        for _try in range(30):
            candidate = random.choice(donor_rows)
            if all(abs((collected - d).days) >= 90 for d in donor_dates[candidate["id"]]):
                donor = candidate
                break
        if donor is None:
            continue

        donor_dates[donor["id"]].append(collected)
        units.append({
            "unit_code": f"U{last_unit + len(units) + 1:03d}",
            "donor_id": donor["id"],
            "blood_group": donor["blood_group"],
            "quantity_ml": random.choices([450, 350], [85, 15])[0],
            "collection_date": collected,
            "expiry_date": collected + timedelta(days=SHELF_LIFE_DAYS),
            "status": pick_status(days_ago),
            "storage_location": random.choice(LOCATIONS),
            "created_at": datetime.combine(collected, time(11, 0)),
        })

    conn.execute(
        text("""
            INSERT INTO blood_inventory
                (unit_code, donor_id, blood_group, quantity_ml, collection_date,
                 expiry_date, status, storage_location, created_at, updated_at)
            VALUES
    (:unit_code, :donor_id, :blood_group, :quantity_ml, :collection_date,
     :expiry_date, :status, :storage_location, :created_at, CURRENT_TIMESTAMP)
        """),
        units,
    )

    # 3. Donor ki last donation date aur eligibility units ke hisaab se
    updates = []
    for d in donor_rows:
        dates = donor_dates[d["id"]]
        if dates:
            last_don = max(dates)
            created = datetime.combine(
                min(dates) - timedelta(days=random.randint(1, 60)), time(10, 0)
            )
            eligible = 1 if (TODAY - last_don).days >= 90 else 0
        else:
            last_don = None
            created = datetime.combine(
                TODAY - timedelta(days=random.randint(1, 200)), time(10, 0)
            )
            eligible = 1
        updates.append({"id": d["id"], "last_don": last_don,
                        "eligible": eligible, "created": created})

    conn.execute(
        text("UPDATE donors SET last_donation_date = :last_don, "
             "is_eligible = :eligible, created_at = :created WHERE id = :id"),
        updates,
    )

print(f"Donors added: {len(donor_rows)}")
print(f"Units added: {len(units)}")
print(dict(Counter(u["status"] for u in units)))