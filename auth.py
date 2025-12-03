# auth.py
import os
import uuid
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt

from database import database, users

# simple logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth")

router = APIRouter()

# Use pbkdf2_sha256 which does not require native bcrypt bindings
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


@router.post("/register")
async def register(req: RegisterRequest):
    try:
        # Check if email exists
        q = users.select().where(users.c.email == req.email)
        existing = await database.fetch_one(q)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password with pbkdf2_sha256 (no 72-byte limit)
        pw_hash = pwd_context.hash(req.password)

        uid = str(uuid.uuid4())

        await database.execute(
            users.insert().values(
                id=uid,
                name=req.name,
                email=req.email,
                password_hash=pw_hash,
                created_at=datetime.utcnow(),
            )
        )

        logger.info("Registered user %s", req.email)
        return {"status": "ok", "message": "User registered successfully"}
    except HTTPException:
        # re-raise HTTPExceptions so FastAPI handles them as-is
        raise
    except Exception as e:
        logger.exception("Failed to register user")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        q = users.select().where(users.c.email == form_data.username)
        user = await database.fetch_one(q)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not pwd_context.verify(form_data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
        expire_ts = int(expire.timestamp())

        sub = str(user["id"])         # ensure UUID (or any non-serializable) becomes JSON string
        token = jwt.encode(
            {"sub": sub, "exp": expire_ts},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        return {"access_token": token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Login failure")
        raise HTTPException(status_code=500, detail="Internal server error")
