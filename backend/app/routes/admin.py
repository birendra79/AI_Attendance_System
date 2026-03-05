from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from .. import schemas, models, database
from ..utils.face_recognition import get_face_encoding
from ..auth import get_current_admin

router = APIRouter()

DbSession = Annotated[Session, Depends(database.get_db)]
CurrentAdmin = Annotated[models.Admin, Depends(get_current_admin)]

@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: DbSession, current_admin: CurrentAdmin):
    # Check if email exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Process the 5 face poses
    def process_encoding(b64_str):
        if not b64_str:
            return None
        encoding = get_face_encoding(b64_str)
        return encoding.tobytes() if encoding is not None else None

    enc_front = process_encoding(user.face_encoding_front_base64)
    if not enc_front:
        raise HTTPException(status_code=400, detail="No face detected in the front image or image missing.")
        
    enc_left = process_encoding(user.face_encoding_left_base64)
    enc_right = process_encoding(user.face_encoding_right_base64)
    enc_up = process_encoding(user.face_encoding_up_base64)
    enc_down = process_encoding(user.face_encoding_down_base64)
    
    new_user = models.User(
        admin_id=current_admin.id,
        name=user.name,
        email=user.email,
        face_encoding_front=enc_front,
        face_encoding_left=enc_left,
        face_encoding_right=enc_right,
        face_encoding_up=enc_up,
        face_encoding_down=enc_down,
        confidence_threshold=user.confidence_threshold
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=List[schemas.UserResponse])
def get_users(db: DbSession, current_admin: CurrentAdmin):
    return db.query(models.User).filter(models.User.admin_id == current_admin.id).all()

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbSession, current_admin: CurrentAdmin):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.admin_id == current_admin.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return None

@router.put("/users/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: DbSession, current_admin: CurrentAdmin):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.admin_id == current_admin.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user_update.name is not None:
        user.name = user_update.name
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.confidence_threshold is not None:
        user.confidence_threshold = user_update.confidence_threshold
        
    db.commit()
    db.refresh(user)
    return user

@router.get("/attendance", response_model=List[schemas.AttendanceLogWithUserResponse])
def get_attendance_logs(db: DbSession, current_admin: CurrentAdmin):
    logs = db.query(models.AttendanceLog).join(models.User).filter(models.User.admin_id == current_admin.id).order_by(models.AttendanceLog.timestamp.desc()).all()
    return logs

import os

@router.get("/system-config")
def get_system_config():
    # Returns the global Ngrok URLs if the user launched start_with_ngrok.py
    # Otherwise returns None, and the frontend can fallback to localhost or LAN IPs
    return {
        "ngrok_backend_url": os.environ.get("NGROK_BACKEND_URL"),
        "ngrok_frontend_url": os.environ.get("NGROK_FRONTEND_URL")
    }

import uuid

# In-memory dictionary to store mobile capture payloads temporarily
mobile_sessions = {}

@router.post("/mobile-session/create")
def create_mobile_session(current_admin: CurrentAdmin):
    session_id = str(uuid.uuid4())
    mobile_sessions[session_id] = {"status": "pending", "data": None}
    return {"session_id": session_id}

@router.get("/mobile-session/{session_id}")
def get_mobile_session(session_id: str, current_admin: CurrentAdmin):
    if session_id not in mobile_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return mobile_sessions[session_id]

@router.post("/mobile-session/{session_id}")
def submit_mobile_session(session_id: str, payload: dict):
    # This endpoint is explicitly left unprotected because the mobile phone reading the QR code
    # doesn't inherently have the admin's JWT token without complicated URL passing.
    # The session_id acts as a one-time obscure token.
    if session_id not in mobile_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    mobile_sessions[session_id]["status"] = "completed"
    mobile_sessions[session_id]["data"] = payload
    return {"message": "Captured successfully"}
