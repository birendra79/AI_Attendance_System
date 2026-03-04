from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
import numpy as np
from datetime import datetime
import face_recognition

from .. import schemas, models, database
from ..utils.face_recognition import get_face_encoding, compare_faces

router = APIRouter()
DbSession = Annotated[Session, Depends(database.get_db)]

from pydantic import BaseModel

class VerifyRequest(BaseModel):
    frame: str
    session_id: int = None

@router.post("/verify")
def verify_attendance(data: VerifyRequest, db: DbSession):
    # Parse image and get encoding
    current_encoding = get_face_encoding(data.frame)
    if current_encoding is None:
        return {"status": "unknown", "reason": "No face detected"}
        
    users = db.query(models.User).all()
    if not users:
        return {"status": "unknown", "reason": "No users in DB"}
        
    best_match_user = None
    best_distance = 1.0 # Lower is better in face_recognition

    for user in users:
        # Build list of valid encodings for this user
        user_encodings = []
        for enc_blob in [user.face_encoding_front, user.face_encoding_left, 
                         user.face_encoding_right, user.face_encoding_up, user.face_encoding_down]:
            if enc_blob:
                user_encodings.append(np.frombuffer(enc_blob, dtype=np.float64))
        
        if not user_encodings:
            continue
            
        # Calculate face distance against all known poses for this user
        distances = face_recognition.face_distance(user_encodings, current_encoding)
        min_dist_for_user = min(distances)
        
        if min_dist_for_user < best_distance:
            best_distance = min_dist_for_user
            best_match_user = user

    # Apply adaptive threshold if set, otherwise global 0.45 
    threshold = best_match_user.confidence_threshold if best_match_user and best_match_user.confidence_threshold else 0.45

    if best_match_user and best_distance <= threshold:
        # Convert distance (0.0=perfect, 0.6=barely passing) to a 100% scale loosely
        # Distance of 0.40 -> ~90%, Distance of 0.20 -> ~96%
        confidence = max(0, min(100, int((1 - (best_distance / 0.6)) * 100)))

        # Log attendance
        log = models.AttendanceLog(
            user_id=best_match_user.id,
            session_id=data.session_id,
            status="Present",
            confidence_score=confidence
        )
        db.add(log)
        db.commit()
        
        return {
            "status": "success",
            "student_name": best_match_user.name,
            "confidence": confidence
        }
        
    return {"status": "spoof", "reason": "Face did not match confidently or spoofing suspected"}
