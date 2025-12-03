from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid

from database import database, payments, rooms

router = APIRouter()

class PaymentRequest(BaseModel):
    room_id: str
    month: int
    year: int
    amount_collected: float = 0
    advance_used: float = 0
    note: str = None


# ---------------------------
# STATUS CALCULATION LOGIC
# ---------------------------
def calculate_status(amount_collected: float, rent_amount: float) -> str:
    today = datetime.utcnow().day

    if amount_collected >= rent_amount:
        return "paid"
    if 0 < amount_collected < rent_amount:
        return "partial"
    if amount_collected == 0:
        return "overdue" if today > 15 else "pending"

    return "pending"


# ---------------------------
# CREATE PAYMENT
# ---------------------------
@router.post("/")
async def add_payment(req: PaymentRequest):

    # Check room
    room = await database.fetch_one(rooms.select().where(rooms.c.id == req.room_id))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Compute status
    status = calculate_status(req.amount_collected, room["rent_amount"])

    pid = str(uuid.uuid4())

    await database.execute(
        payments.insert().values(
            id=pid,
            room_id=req.room_id,
            month=req.month,
            year=req.year,
            status=status,
            amount_collected=req.amount_collected,
            advance_used=req.advance_used,
            note=req.note,
            created_at=datetime.utcnow()
        )
    )

    return {"status": "ok", "payment_id": pid, "payment_status": status}


# ---------------------------
# GET PAYMENTS
# ---------------------------
@router.get("/")
async def list_payments(room_id: str):
    query = payments.select().where(payments.c.room_id == room_id)
    items = await database.fetch_all(query)
    return items


# ---------------------------
# UPDATE PAYMENT
# ---------------------------
class PaymentUpdate(BaseModel):
    amount_collected: float = None
    advance_used: float = None
    note: str = None


@router.patch("/{payment_id}")
async def update_payment(payment_id: str, req: PaymentUpdate):

    payment = await database.fetch_one(
        payments.select().where(payments.c.id == payment_id)
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    room = await database.fetch_one(
        rooms.select().where(rooms.c.id == payment["room_id"])
    )

    new_amount = req.amount_collected if req.amount_collected is not None else payment["amount_collected"]
    new_advance = req.advance_used if req.advance_used is not None else payment["advance_used"]

    new_status = calculate_status(new_amount, room["rent_amount"])

    await database.execute(
        payments.update()
        .where(payments.c.id == payment_id)
        .values(
            amount_collected=new_amount,
            advance_used=new_advance,
            note=req.note if req.note is not None else payment["note"],
            status=new_status,
        )
    )

    return {"status": "updated", "payment_status": new_status}
