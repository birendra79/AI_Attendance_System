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

def is_image_blurry(img: np.ndarray, threshold: float = 100.0) -> bool:
    """
    Check if an image is blurry using the variance of the Laplacian method.
    A lower threshold means less strict. 100.0 is a reasonable default.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    return fm < threshold

def check_liveness(img: np.ndarray) -> bool:
    """
    Perform a basic liveness/anti-spoofing check.
    For this basic implementation, we look for eyes using a Haar Cascade.
    If a face is detected by the main engine but no eyes are found (e.g., flat mask or poor quality photo), we may flag it.
    Returns True if liveness is likely, False if spoofing is suspected.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Load the eye cascade classifier
    eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    
    # Detect eyes
    eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20))
    
    # Simple heuristic: If we can see at least one eye, we assume it's live (pass)
    # A flat, shiny photo held to a camera often fails to produce clear eye features that pass the cascade
    return len(eyes) > 0
