# Standard library imports
from typing import Dict, Any

# Third-party imports
from fastapi import APIRouter, Request, Body, Depends

# Local imports
from models import AuthCredentials
from utils import (
    load_users_from_db, save_users_in_db, hash_password,
    verify_password, generate_avatar, session_users
)

auth_router = APIRouter()

@auth_router.post("/signup")
async def signup(request: Request,
                 credentials: AuthCredentials = Body(...),
                 users: Dict[str, Any] = Depends(load_users_from_db)
                 ) -> Dict[str, Any]:
    username = credentials.username
    password = credentials.password
    if username in users:
        return {"error": "Username already exists."}
    users[username] = hash_password(password)
    save_users_in_db(users)
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
                users: Dict[str, Any] = Depends(load_users_from_db)
                ) -> Dict[str, Any]:
    username = credentials.username
    password = credentials.password
    if username not in users or not verify_password(password, users[username]):
        return {"error": "Invalid username or password."}
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