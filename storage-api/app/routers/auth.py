from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models import Admin
from app.schemas import LoginRequest, TokenResponse, AdminResponse
from app.security import verify_password, create_access_token, get_current_admin

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    admin = session.query(Admin).filter(Admin.username == data.username).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return TokenResponse(access_token=create_access_token(admin.username))

@router.get("/me", response_model=AdminResponse)
def me(admin: Admin = Depends(get_current_admin)):
    return admin
