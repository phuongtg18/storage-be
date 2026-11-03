import os
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models import Admin
from app.security import hash_password
from app.routers import auth, items, categories, stock, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "")
    if not password:
        raise RuntimeError("Set ADMIN_PASSWORD in .env before starting the API")
    with Session(engine) as session:
        admin = session.exec(select(Admin).where(Admin.username == username)).first()
        if not admin:
            session.add(Admin(username=username, password_hash=hash_password(password)))
            session.commit()
    yield

app = FastAPI(
    title="Storage Manager API",
    description="Inventory, stock transactions and dashboard API",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(stock.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"name": "Storage Manager API", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok"}
