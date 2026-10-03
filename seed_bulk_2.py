import random
from collections import Counter, defaultdict
from datetime import date, datetime, time

from sqlalchemy import text

from database import engine

random.seed(11)
TODAY = date.today()

HOSPITALS = [
    "Ruby Hall Clinic, Pune", "Sahyadri Hospital, Pune", "Jehangir Hospital, Pune",
    "Deenanath Mangeshkar Hospital, Pune", "Sassoon General Hospital, Pune",
    "Lilavati Hospital, Mumbai", "KEM Hospital, Mumbai", "Hinduja Hospital, Mumbai",
    "Kokilaben Hospital, Mumbai", "Nanavati Hospital, Mumbai",
    "Tata Memorial Hospital, Mumbai", "Wockhardt Hospital, Nagpur",
    "Apollo Hospital, Hyderabad", "KIMS Hospital, Hyderabad",
    "Manipal Hospital, Bengaluru", "Narayana Health, Bengaluru",
    "Fortis Hospital, Chennai", "AIIMS, Delhi", "Sir Ganga Ram Hospital, Delhi",
    "Medanta, Gurugram", "SMS Hospital, Jaipur", "Aster Medcity, Kochi",
    "Civil Hospital, Ahmedabad",
]
FIRST = ["Ramesh", "Sunita", "Mohan", "Fatima", "Deepak", "Lakshmi", "Sanjay", "Meena",
         "Imran", "Rekha", "Anil", "Geeta", "Vijay", "Asha", "Prakash", "Shobha",
         "Ajay", "Nirmala", "Dinesh", "Usha", "Harish", "Kamala", "Ravi", "Savita",
         "Ashok", "Pushpa", "Naresh", "Leela", "Bharat", "Sarita"]
LAST = ["Kadam", "Bhosale", "Rao", "Sheikh", "Yadav", "Iyer", "Pawar", "Kulkarni",
        "Khan", "Menon", "Patil", "Joshi", "Sharma", "Singh", "Gupta", "Nair", "Reddy",
        "Shinde", "Jadhav", "More", "Desai", "Verma", "Chavan", "Thakur", "Das"]
GROUPS = ["O+", "B+", "A+", "AB+", "O-", "B-", "A-", "AB-"]
WEIGHTS = [33, 30, 21, 7, 3, 2.5, 2.5, 1]


def make_patient():
    return f"{random.choice(FIRST)} {random.choice(LAST)}"


def random_time():
    return time(random.randint(8, 18), random.randint(0, 59))


def pick_urgency(weights):
    return random.choices(["Normal", "Urgent", "Emergency"], weights)[0]


def batch_size():
    return random.choices([1, 2, 3], [55, 30, 15])[0]


with engine.begin() as conn:
    existing = conn.execute(text("SELECT COUNT(*) FROM blood_requests")).scalar()
    if existing > 50:
        print("Bulk requests already exist. Stopping.")
        raise SystemExit

    user_ids = [r[0] for r in conn.execute(text("SELECT id FROM users WHERE is_active = 1"))]
    last_request = conn.execute(
        text("SELECT MAX(CAST(SUBSTRING(request_code, 2) AS UNSIGNED)) FROM blood_requests")
    ).scalar() or 0
    last_dist = conn.execute(
        text("SELECT MAX(CAST(SUBSTRING(distribution_code, 4) AS UNSIGNED)) FROM blood_distribution")
    ).scalar() or 0

    # Jo units Issued hain par distribution record nahi hai
    issued = [dict(r) for r in conn.execute(text("""
        SELECT i.id, i.blood_group, i.quantity_ml, i.collection_date, i.expiry_date
        FROM blood_inventory i
        LEFT JOIN blood_distribution d ON d.inventory_id = i.id
        WHERE i.status = 'Issued' AND d.id IS NULL
    """)).mappings().all()]

    # Same group ke nazdeeki units ko 1-3 ke batch mein baanto
    by_group = defaultdict(list)
    for u in issued:
        by_group[u["blood_group"]].append(u)

    batches = []
    for units in by_group.values():
        units.sort(key=lambda u: u["collection_date"])
        current, target = [], batch_size()
        for u in units:
            too_far = current and (u["collection_date"] - current[0]["collection_date"]).days > 10
            if current and (len(current) >= target or too_far):
                batches.append(current)
                current, target = [], batch_size()
            current.append(u)
        if current:
            batches.append(current)

    all_requests = []

    for batch in batches:
        low = max(u["collection_date"] for u in batch)
        high = min(min(u["expiry_date"] for u in batch), TODAY)
        span = max((high - low).days, 0)
        issue_date = low + (TODAY - TODAY) + __import__("datetime").timedelta(
            days=random.randint(0, min(span, 20))
        )
        back = random.randint(0, min(2, (issue_date - low).days))
        request_date = issue_date - __import__("datetime").timedelta(days=back)
        all_requests.append({
            "status": "Fulfilled",
            "group": batch[0]["blood_group"],
            "units": len(batch),
            "urgency": pick_urgency([70, 20, 10]),
            "request_date": request_date,
            "issue_date": issue_date,
            "batch": batch,
        })

    td = __import__("datetime").timedelta

    for _ in range(20):   # Pending
        all_requests.append({
            "status": "Pending", "group": random.choices(GROUPS, WEIGHTS)[0],
            "units": random.randint(1, 3), "urgency": pick_urgency([50, 30, 20]),
            "request_date": TODAY - td(days=random.randint(0, 6)), "batch": None,
        })
    for _ in range(12):   # Approved (sirf common groups, taaki Fulfill ho sake)
        all_requests.append({
            "status": "Approved", "group": random.choice(["O+", "B+", "A+"]),
            "units": random.randint(1, 2), "urgency": pick_urgency([50, 35, 15]),
            "request_date": TODAY - td(days=random.randint(1, 7)), "batch": None,
        })
    for _ in range(13):   # Rejected
        all_requests.append({
            "status": "Rejected", "group": random.choices(GROUPS, WEIGHTS)[0],
            "units": random.randint(1, 3), "urgency": pick_urgency([70, 20, 10]),
            "request_date": TODAY - td(days=random.randint(3, 60)), "batch": None,
        })

    all_requests.sort(key=lambda r: r["request_date"])

    dist_no = last_dist
    for n, r in enumerate(all_requests, start=last_request + 1):
        hospital = random.choice(HOSPITALS)
        patient = make_patient()
        res = conn.execute(
            text("""
                INSERT INTO blood_requests
                    (request_code, patient_name, patient_age, hospital_name, blood_group,
                     units_required, urgency, status, requested_by, request_date,
                     created_at, updated_at)
                VALUES
                    (:code, :patient, :age, :hospital, :group, :units, :urgency,
                     :status, :by, :rdate, :created, NOW())
            """),
            {
                "code": f"R{n:03d}", "patient": patient, "age": random.randint(3, 80),
                "hospital": hospital, "group": r["group"], "units": r["units"],
                "urgency": r["urgency"], "status": r["status"],
                "by": random.choice(user_ids), "rdate": r["request_date"],
                "created": datetime.combine(r["request_date"], random_time()),
            },
        )

        if r["batch"]:
            req_id = res.lastrowid
            rows = []
            for u in r["batch"]:
                dist_no += 1
                rows.append({
                    "code": f"DIS{dist_no:03d}", "req": req_id, "inv": u["id"],
                    "hospital": hospital, "patient": patient, "qty": u["quantity_ml"],
                    "idate": r["issue_date"], "by": random.choice(user_ids),
                    "created": datetime.combine(r["issue_date"], random_time()),
                })
            conn.execute(
                text("""
                    INSERT INTO blood_distribution
                        (distribution_code, request_id, inventory_id, hospital_name,
                         patient_name, quantity_ml, issue_date, issued_by, status,
                         created_at, updated_at)
                    VALUES
                        (:code, :req, :inv, :hospital, :patient, :qty, :idate, :by,
                         'Completed', :created, NOW())
                """),
                rows,
            )

print(f"Requests added: {len(all_requests)}")
print(dict(Counter(r["status"] for r in all_requests)))
print(f"Distribution records added: {dist_no - last_dist}")