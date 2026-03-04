# AI Attendance System

A comprehensive facial recognition-based attendance system built with FastAPI (Backend) and Vanilla HTML/JS with Bootstrap (Frontend).

## Features
- **Backend**: FastAPI providing robust and high-performance routing.
- **Database**: SQLite with SQLAlchemy to store registered users and attendance logs.
- **Face Recognition**: Utilizing `face_recognition` library to generate facial encodings and compare them.
- **Admin Dashboard**: View all registered users and a real-time attendance log.
- **Registration Kiosk**: Capture an employee's face via webcam to enroll them into the system.
- **Verification Kiosk**: Automated kiosk that scans faces on an interval to seamlessly record attendance without clicking buttons.

## Project Structure
- `backend/`: FastAPI application containing all models, schemas, and routes.
- `frontend-admin/`: HTML pages serving the admin side (Dashboard and Registration).
- `frontend-verification/`: HTML page serving the kiosk side for marking attendance.

## Installation and Execution

### 1. Backend Setup
1. CD into the backend directory.
2. Create standard python virtual environment (if not already using the parent one).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the API Server:
   ```bash
   uvicorn app.main:app --reload
   ```

### 2. Frontend Usage
Simply open these static files directly in any modern web browser (Edge, Chrome, Safari). Ensure the backend is running on `127.0.0.1:8000` for API calls to work.

- **Admin Dashboard:** Open `frontend-admin/dashboard.html`
- **Register User:** Open `frontend-admin/register.html`
- **Mark Attendance:** Open `frontend-verification/verify.html`

*Note: For webcam access to work securely, ensure your browser permits getUserMedia. Running locally via `file://` usually bypasses the HTTPS requirement, otherwise use a local HTTP server.*
