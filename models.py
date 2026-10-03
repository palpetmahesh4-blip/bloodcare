from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="staff")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    donor_code = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    gender = Column(String(10), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    blood_group = Column(String(3), nullable=False, index=True)
    phone = Column(String(15), nullable=False)
    email = Column(String(120))
    city = Column(String(60), nullable=False)
    last_donation_date = Column(Date)
    is_eligible = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BloodInventory(Base):
    __tablename__ = "blood_inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_code = Column(String(20), unique=True, nullable=False)
    donor_id = Column(Integer, ForeignKey("donors.id"), nullable=False)
    blood_group = Column(String(3), nullable=False, index=True)
    quantity_ml = Column(Integer, nullable=False, default=450)
    collection_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="Available", index=True)
    storage_location = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_code = Column(String(20), unique=True, nullable=False)
    patient_name = Column(String(100), nullable=False)
    patient_age = Column(Integer)
    hospital_name = Column(String(120), nullable=False)
    blood_group = Column(String(3), nullable=False, index=True)
    units_required = Column(Integer, nullable=False, default=1)
    urgency = Column(String(20), nullable=False, default="Normal")
    status = Column(String(20), nullable=False, default="Pending", index=True)
    requested_by = Column(Integer, ForeignKey("users.id"))
    request_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BloodDistribution(Base):
    __tablename__ = "blood_distribution"

    id = Column(Integer, primary_key=True, autoincrement=True)
    distribution_code = Column(String(20), unique=True, nullable=False)
    request_id = Column(Integer, ForeignKey("blood_requests.id"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("blood_inventory.id"), nullable=False)
    hospital_name = Column(String(120), nullable=False)
    patient_name = Column(String(100), nullable=False)
    quantity_ml = Column(Integer, nullable=False, default=450)
    issue_date = Column(Date, nullable=False)
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False, default="Completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(30), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="info")
    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(60), nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)