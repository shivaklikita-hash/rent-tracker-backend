from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
import uuid
from database import database, users

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
SECRET_KEY = os.getenv('SECRET_KEY') or 'change-this'
ALGORITHM = os.getenv('ALGORITHM') or 'HS256'
ACCESS_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES') or 1440)

router = APIRouter()

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

@router.post('/register')
async def register(req: RegisterRequest):
    q = users.select().where(users.c.email == req.email)
    existing = await database.fetch_one(q)
    if existing:
        raise HTTPException(status_code=400, detail='Email exists')
    pw = pwd_context.hash(req.password)
    uid = str(uuid.uuid4())
    await database.execute(users.insert().values(id=uid, name=req.name, email=req.email, password_hash=pw))
    return {'status':'ok'}

from fastapi.security import OAuth2PasswordRequestForm

@router.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    q = users.select().where(users.c.email == form_data.username)
    user = await database.fetch_one(q)
    if not user or not pwd_context.verify(form_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MINUTES)
    token = jwt.encode({'sub': user['id'], 'exp': expire.isoformat()}, SECRET_KEY, algorithm=ALGORITHM)
    return {'access_token': token, 'token_type':'bearer'}
