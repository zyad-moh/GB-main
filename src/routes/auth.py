from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, EmailStr
from jose import jwt
from datetime import datetime, timedelta
import os

ACCESS_SECRET="askjdhaskjdhkajshd"
REFRESH_SECRET="qweqweqweqweqwe"
JWT_SECRET="my_secret_key"



def create_access_token(user: dict):
    payload = {
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }

    return jwt.encode(
        payload,
        ACCESS_SECRET,
        algorithm="HS256"
    )


def create_refresh_token(user: dict):
    payload = {
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(days=7)
    }

    return jwt.encode(
        payload,
        REFRESH_SECRET,
        algorithm="HS256"
    )


auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"]
)

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role:str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@auth_router.post("/signup")
async def signup(request: Request, data: SignupRequest):

    project_collection = request.app.db_client.projects

    existing_user = await project_collection.find_one({
        "email": data.email
    })

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    """last_project = await project_collection.find_one(
        sort=[("project_id", -1)]
    )"""
    projects = await project_collection.find(
    {},
    {"project_id": 1}
    ).to_list(length=None)

    max_id = max(
        [int(p["project_id"]) for p in projects],
        default=0
    )

    next_project_id = max_id + 1
    """next_project_id = (
        int(last_project["project_id"] )+ 1
        if last_project and "project_id" in last_project
        else 1
    )"""

    await project_collection.insert_one({
        "project_id": str(next_project_id),
        "email": data.email,
        "password": data.password,   # 👈 plain text
        "role": data.role
    })

    return {
        "message": "User created successfully",
        "user_id": str(next_project_id)
    }

@auth_router.post("/login")
async def login(request: Request, data: LoginRequest):

    project_collection = request.app.db_client.projects

    user = await project_collection.find_one({
        "email": data.email
    })

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credenttttttials"
        )

    if data.password != user["password"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    return {
        "message": "Login successful",
        "user_id": user["project_id"],
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@auth_router.get("/me")
def get_me():
    return {"message": "You are authorized"}