from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Admin Schemas
class AdminCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ForgotUsernameRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    face_encoding_front_base64: str  # Base64 encoded image string
    face_encoding_left_base64: Optional[str] = None
    face_encoding_right_base64: Optional[str] = None
    face_encoding_up_base64: Optional[str] = None
    face_encoding_down_base64: Optional[str] = None
    confidence_threshold: Optional[float] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    confidence_threshold: Optional[float] = None

class UserResponse(UserBase):
    id: int
    registration_date: datetime
    confidence_threshold: Optional[float] = None

    class Config:
        from_attributes = True

# Session Schemas
class ClassSessionBase(BaseModel):
    name: str
    is_active: Optional[bool] = True

class ClassSessionCreate(ClassSessionBase):
    pass

class ClassSessionResponse(ClassSessionBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True

# Attendance Schemas
class AttendanceLogBase(BaseModel):
    pass

class AttendanceLogCreate(BaseModel):
    face_image_base64: str  # Base64 encoded image string
    session_id: Optional[int] = None
    confidence_score: Optional[float] = None

class AttendanceLogResponse(BaseModel):
    id: int
    user_id: int
    session_id: Optional[int] = None
    timestamp: datetime
    status: str
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True

class AttendanceLogWithUserResponse(AttendanceLogResponse):
    user: UserResponse

    class Config:
        from_attributes = True

# Audit & Spoof Schemas
class AuditLogResponse(BaseModel):
    id: int
    admin_id: Optional[int] = None
    action: str
    details: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True

class SpoofLogResponse(BaseModel):
    id: int
    timestamp: datetime
    reason: str
    session_id: Optional[int] = None
    # omitting the large binary capture_image from default response list

    class Config:
        from_attributes = True

# Dispute Schemas
class DisputeCreate(BaseModel):
    user_id: int
    attendance_log_id: int
    reason: str

class DisputeResponse(BaseModel):
    id: int
    user_id: int
    attendance_log_id: int
    reason: str
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True
