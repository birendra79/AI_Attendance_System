import face_recognition
import numpy as np
import base64
import cv2
import io
from typing import Optional

def decode_base64_image(base64_str: str) -> np.ndarray:
    """Decode a base64 encoded string to cv2 image format."""
    # Handle data URI prefix, if any
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    
    img_bytes = base64.b64decode(base64_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def get_face_encoding(image_base64: str) -> Optional[np.ndarray]:
    """Get the face encoding from a base64 image."""
    try:
        img = decode_base64_image(image_base64)
    except Exception:
        return None

    if img is None:
        return None

    # Convert BGR to RGB
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect face
    encodings = face_recognition.face_encodings(rgb_img)
    if len(encodings) > 0:
        return encodings[0]
    return None

def compare_faces(known_encondings: list[np.ndarray], face_encoding_to_check: np.ndarray, tolerance: float = 0.6) -> list[bool]:
    """Compare faces to find a match."""
    return face_recognition.compare_faces(known_encondings, face_encoding_to_check, tolerance=tolerance)
