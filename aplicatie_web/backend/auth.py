# Standard library imports
from typing import Dict

# Third-party imports
from fastapi import APIRouter, Request, Body, Depends, HTTPException
from sqlalchemy.orm import Session

# Local imports
from schemas import AuthCredentials
from utils import hash_password, verify_password, generate_avatar, session_users
from models_orm import User
from database import get_db

auth_router = APIRouter()

@auth_router.post("/signup")
async def signup(request: Request,
                 credentials: AuthCredentials = Body(...),
                 db: Session = Depends(get_db)):
    username = credentials.username
    password = credentials.password

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists.")
    new_user = User(username=username, password_hash=hash_password(password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    session_users[request.state.session_id] = username

    return {
        "message": "User registered successfully.",
        "username": username,
        "avatar": generate_avatar(username),
        "logged_in": True
    }

@auth_router.post("/login")
async def login(request: Request,
                credentials: AuthCredentials = Body(...),
                db: Session = Depends(get_db)):
    username = credentials.username
    password = credentials.password

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    session_users[request.state.session_id] = username
    return {
        "message": f"User logged in successfully.",
        "username": username,
        "avatar": generate_avatar(username),
        "logged_in": True
    }

@auth_router.post("/logout")
async def logout(request: Request) -> Dict[str, str]:
    session_id = request.state.session_id
    session_users.pop(session_id, None)
    return {"message": "User logged out successfully."}