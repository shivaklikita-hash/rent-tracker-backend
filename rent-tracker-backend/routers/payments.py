from fastapi import APIRouter, HTTPException
from database import database, payments
import uuid
from pydantic import BaseModel

router = APIRouter()

class PaymentIn(BaseModel):
    room_id: str
    month: int
    year: int
    status: str
    amount_collected: float = 0
    advance_used: float = 0
    note: str = None

@router.post('/')
async def record_payment(p: PaymentIn):
    pid = str(uuid.uuid4())
    try:
        await database.execute(payments.insert().values(
            id=pid,
            room_id=p.room_id,
            month=p.month,
            year=p.year,
            status=p.status,
            amount_collected=p.amount_collected,
            advance_used=p.advance_used,
            note=p.note
        ))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {'id': pid}

@router.get('/')
async def list_payments(room_id: str = None, month: int = None, year: int = None):
    q = payments.select()
    if room_id:
        q = q.where(payments.c.room_id == room_id)
    if month:
        q = q.where(payments.c.month == month)
    if year:
        q = q.where(payments.c.year == year)
    res = await database.fetch_all(q)
    return res
