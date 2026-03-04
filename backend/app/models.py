from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Boolean, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)
    is_verified = Column(Integer, default=0)
    confirm_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    
    # Updated: Store 5 poses for multi-angle face enrollment
    face_encoding_front = Column(LargeBinary, nullable=False)
    face_encoding_left = Column(LargeBinary, nullable=True)
    face_encoding_right = Column(LargeBinary, nullable=True)
    face_encoding_up = Column(LargeBinary, nullable=True)
    face_encoding_down = Column(LargeBinary, nullable=True)
    
    # Adaptive confidence threshold for this specific student
    confidence_threshold = Column(Float, nullable=True) 

    registration_date = Column(DateTime, default=datetime.utcnow)

    attendance_logs = relationship("AttendanceLog", back_populates="user")
    disputes = relationship("Dispute", back_populates="user")

class ClassSession(Base):
    __tablename__ = "class_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # e.g. "CS101 - Morning"
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    attendance_logs = relationship("AttendanceLog", back_populates="session")

class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String) # "Present", "Absent", "Late", "Manual Override"
    confidence_score = Column(Float, nullable=True)

    user = relationship("User", back_populates="attendance_logs")
    session = relationship("ClassSession", back_populates="attendance_logs")

class AuditLog(Base):
    """Immutable ledger for system changes and manual overrides"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    action = Column(String, nullable=False) # e.g., "Updated Student Threshold", "Manual Attendance Override"
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)

class SpoofLog(Base):
    """Tracks failed liveness checks / spoofing attempts"""
    __tablename__ = "spoof_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    reason = Column(String) # e.g., "No Blink Detected", "Deepfake Probability High"
    capture_image = Column(LargeBinary, nullable=True) # The exact frame that failed
    session_id = Column(Integer, ForeignKey("class_sessions.id"), nullable=True)

class Dispute(Base):
    """Student disputes for attendance records"""
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    attendance_log_id = Column(Integer, ForeignKey("attendance_logs.id"))
    reason = Column(Text, nullable=False)
    status = Column(String, default="Pending") # Pending, Approved, Rejected
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="disputes")
