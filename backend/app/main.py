from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import admin, verification
from . import auth
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables on startup
    Base.metadata.create_all(bind=engine)
    yield
    # No shutdown logic needed for now

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(verification.router, prefix="/api/verify", tags=["verification"])

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# Triggering uvicorn reload to pick up new .env Supabase pooler variables!
