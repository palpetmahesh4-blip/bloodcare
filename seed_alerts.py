from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import engine
from models import User, Notification, ActivityLog

with Session(engine) as session:
    if session.query(Notification).count() > 0 or session.query(ActivityLog).count() > 0:
        print("Alerts/logs already exist, skipping.")
    else:
        admin = session.query(User).filter_by(email="admin@bloodbank.in").first()
        staff = session.query(User).filter_by(email="staff@bloodbank.in").first()
        now = datetime.utcnow()

        notifications = [
            ("Emergency request", "R004: O- blood, 3 units needed at KEM Hospital, Mumbai.", "request", "danger", False),
            ("Emergency request", "R007: O+ blood, 2 units needed at Sahyadri Hospital, Pune.", "request", "danger", False),
            ("Low stock alert", "AB- and B- stock is very low (1 unit each).", "stock", "warning", False),
            ("Blood expiring soon", "Units U008, U009 and U010 expire within 7 days.", "expiry", "warning", False),
            ("Expired blood", "Unit U011 (A-) has expired and needs to be discarded.", "expiry", "danger", True),
            ("Pending requests", "5 blood requests are waiting for approval.", "request", "info", True),
        ]
        for title, message, category, severity, is_read in notifications:
            session.add(Notification(
                title=title, message=message, category=category,
                severity=severity, is_read=is_read,
            ))

        logs = [
            (admin.id, "LOGIN", "Admin logged in", now - timedelta(hours=5)),
            (staff.id, "ADD_UNIT", "Added blood unit U016 (O+)", now - timedelta(hours=4)),
            (staff.id, "CREATE_REQUEST", "Created request R004 (O-, Emergency)", now - timedelta(hours=3)),
            (admin.id, "APPROVE_REQUEST", "Approved request R003", now - timedelta(hours=2)),
            (staff.id, "ISSUE_BLOOD", "Issued unit U013 for request R002", now - timedelta(hours=1)),
            (admin.id, "DISCARD_UNIT", "Discarded unit U015 (O-)", now - timedelta(minutes=30)),
        ]
        for user_id, action, details, created in logs:
            session.add(ActivityLog(
                user_id=user_id, action=action, details=details, created_at=created,
            ))

        session.commit()
        print("Added 6 notifications and 6 activity logs.")

print("Done!")