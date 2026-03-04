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
    return db.query(models.User).all()

@router.get("/attendance", response_model=List[schemas.AttendanceLogWithUserResponse])
def get_attendance_logs(db: DbSession, current_admin: CurrentAdmin):
    logs = db.query(models.AttendanceLog).order_by(models.AttendanceLog.timestamp.desc()).all()
    return logs
