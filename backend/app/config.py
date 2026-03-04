from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Attendance System API"
    DATABASE_URL: str = "sqlite:///./attendance.db"
    SECRET_KEY: str = "supersecretkey"

    # SMTP / Email Settings — set these in your .env file
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""        # e.g. yourname@gmail.com
    SMTP_PASSWORD: str = ""        # Gmail App Password (16 chars)
    EMAIL_FROM: str = ""           # same as SMTP_USERNAME usually

    # Frontend base URL so email links work correctly
    FRONTEND_URL: str = "http://127.0.0.1:5500"  # VS Code Live Server default

    class Config:
        env_file = ".env"

settings = Settings()
