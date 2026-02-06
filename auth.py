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
from sqlalchemy import func

from database import database, users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth")

router = APIRouter()

# password hashing — matches your stored hashes
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

SECRET_KEY = os.getenv("SECRET_KEY", "change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))


# =========================
# Models
# =========================

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


# =========================
# Register
# =========================

@router.post("/register")
async def register(req: RegisterRequest):
    try:
        # check existing user (case insensitive)
        q = users.select().where(
            func.lower(users.c.email) == req.email.lower()
        )
        existing = await database.fetch_one(q)

        if existing:
            raise HTTPException(400, "Email already registered")

        pw_hash = pwd_context.hash(req.password)
        uid = str(uuid.uuid4())

        await database.execute(
            users.insert().values(
                id=uid,
                name=req.name,
                email=req.email.lower(),
                password_hash=pw_hash,
            )
        )

        logger.info("Registered user %s", req.email)
        return {"status": "ok", "message": "User registered successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Register failure: %s", e)
        raise HTTPException(500, str(e))


# =========================
# Login (OAuth2 form)
# =========================

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # case-insensitive email match
        q = users.select().where(
            func.lower(users.c.email) == form_data.username.lower()
        )

        user = await database.fetch_one(q)

        if not user:
            raise HTTPException(401, "Invalid email or password")

        hash_value = user.get("password_hash")
        if not hash_value:
            raise HTTPException(401, "Invalid email or password")

        try:
            ok = pwd_context.verify(form_data.password, hash_value)
        except Exception as e:
            logger.exception("Password verify crash: %s", e)
            raise HTTPException(401, "Invalid email or password")

        if not ok:
            raise HTTPException(401, "Invalid email or password")

        expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)

        token = jwt.encode(
            {
                "sub": str(user["id"]),
                "exp": int(expire.timestamp()),
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Login failure: %s", e)
        raise HTTPException(500, str(e))
