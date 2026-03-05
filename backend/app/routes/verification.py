from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
import numpy as np
from datetime import datetime
import face_recognition

from .. import schemas, models, database
from ..utils.face_recognition import get_face_encoding, compare_faces

from ..utils.face_recognition import get_face_encoding, compare_faces, decode_base64_image, is_image_blurry, check_liveness
import cv2

router = APIRouter()
DbSession = Annotated[Session, Depends(database.get_db)]

from pydantic import BaseModel

class VerifyRequest(BaseModel):
    frame: str
    session_id: int = None

@router.post("/verify")
def verify_attendance(data: VerifyRequest, db: DbSession):
    # Decode image securely for heuristics
    try:
        img = decode_base64_image(data.frame)
        if img is None:
            return {"status": "unknown", "reason": "Corrupted image frame"}
    except Exception:
        return {"status": "unknown", "reason": "Failed to decode image"}
        
    # 1. Fog/Blur Detection
    # Calculate exact variance to pass to the adaptive threshold later
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    if variance < 80.0: # Moderate blur threshold
        return {"status": "poor_quality", "reason": "Environment is too foggy or camera is blurry. Please wipe the lens or step closer."}
        
    # 2. Anti-Spoofing Liveness Check
    if not check_liveness(img):
        return {"status": "spoof", "reason": "Liveness check failed. Please remove masks and ensure your eyes are clearly visible."}

    # 3. Parse image and get encoding
    current_encoding = get_face_encoding(data.frame)
    if current_encoding is None:
        return {"status": "unknown", "reason": "No face detected by recognition engine"}
        
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
    # If the variance is extremely high (very sharp), allow a slightly looser threshold because we trust the crisp edges.
    # If variance is somewhat low, tighten the threshold to prevent false positives in noisy images.
    base_thresh = best_match_user.confidence_threshold if best_match_user and best_match_user.confidence_threshold else 0.45
    adaptive_threshold = base_thresh + 0.05 if variance > 500 else base_thresh - 0.05

    if best_match_user and best_distance <= adaptive_threshold:
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
