from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserOut, Token
from ..auth import hash_password, verify_password, create_token, current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(400, "Email already registered")
    user = User(email=email, password_hash=hash_password(data.password), role=data.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(data: UserCreate, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_token(user))

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
