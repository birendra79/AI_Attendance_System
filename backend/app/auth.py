import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Annotated

from . import database, models, schemas, security
from .utils.email import send_username_email, send_password_reset_email

router = APIRouter()
DbSession = Annotated[Session, Depends(database.get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


@router.post("/signup", status_code=status.HTTP_202_ACCEPTED)
def signup(admin_data: schemas.AdminCreate, db: DbSession):
    # Check username taken
    if db.query(models.Admin).filter(models.Admin.username == admin_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    # Check email taken
    if db.query(models.Admin).filter(models.Admin.email == admin_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    token = secrets.token_urlsafe(32)
    hashed_pwd = security.get_password_hash(admin_data.password)

    new_admin = models.Admin(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=hashed_pwd,
        is_verified=1,
        confirm_token=None
    )
    db.add(new_admin)
    db.commit()

    return {"message": "Signup successful! You can now log in."}


@router.get("/confirm/{token}")
def confirm_email(token: str, db: DbSession):
    admin = db.query(models.Admin).filter(models.Admin.confirm_token == token).first()
    if not admin:
        raise HTTPException(status_code=400, detail="Invalid or expired confirmation token.")
    if admin.is_verified:
        return {"message": "Account already confirmed. You can log in."}

    admin.is_verified = 1
    admin.confirm_token = None
    db.commit()
    return {"message": "Email confirmed! You can now log in."}


@router.post("/login", response_model=schemas.Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    admin = db.query(models.Admin).filter(models.Admin.username == form_data.username).first()
    if not admin or not security.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-username")
def forgot_username(request: schemas.ForgotUsernameRequest, db: DbSession):
    admin = db.query(models.Admin).filter(models.Admin.email == request.email).first()
    if admin:
        try:
            send_username_email(admin.email, admin.username)
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
    # Always return same response for security (don't reveal if email exists)
    return {"message": "If that email is registered, your username has been sent."}


@router.post("/forgot-password")
def forgot_password(request: schemas.ForgotPasswordRequest, db: DbSession):
    admin = db.query(models.Admin).filter(models.Admin.email == request.email).first()
    if admin:
        token = secrets.token_urlsafe(32)
        admin.reset_token = token
        admin.reset_token_expiry = datetime.utcnow() + timedelta(minutes=30)
        db.commit()
        try:
            send_password_reset_email(admin.email, admin.username, token)
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
    return {"message": "If that email is registered, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(request: schemas.ResetPasswordRequest, db: DbSession):
    admin = db.query(models.Admin).filter(models.Admin.reset_token == request.token).first()
    if not admin or admin.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

    admin.hashed_password = security.get_password_hash(request.new_password)
    admin.reset_token = None
    admin.reset_token_expiry = None
    db.commit()
    return {"message": "Password reset successfully! You can now log in."}


def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, security.settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except security.jwt.PyJWTError:
        raise credentials_exception

    admin = db.query(models.Admin).filter(models.Admin.username == username).first()
    if admin is None:
        raise credentials_exception
    return admin
