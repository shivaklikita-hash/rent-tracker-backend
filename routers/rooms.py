from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from database import database, rooms as rooms_table

router = APIRouter()

class RoomCreate(BaseModel):
    floor_id: str
    room_number: str
    tenant_name: str | None = None
    rent_amount: float | None = 0
    advance_amount: float | None = 0

class RoomUpdate(BaseModel):
    room_number: str | None = None
    tenant_name: str | None = None
    rent_amount: float | None = None
    advance_amount: float | None = None

@router.get("/")
async def list_rooms(floor_id: str):
    q = rooms_table.select().where(rooms_table.c.floor_id == floor_id)
    rows = await database.fetch_all(q)
    return [dict(r) for r in rows]

@router.post("/")
async def create_room(payload: RoomCreate):
    rid = str(uuid.uuid4())
    await database.execute(rooms_table.insert().values(
        id=rid,
        floor_id=payload.floor_id,
        room_number=payload.room_number,
        tenant_name=payload.tenant_name,
        rent_amount=payload.rent_amount or 0,
        advance_amount=payload.advance_amount or 0
    ))
    return {"id": rid}

@router.put("/{room_id}")
async def update_room(room_id: str, payload: RoomUpdate):
    values = {k: v for k, v in payload.dict().items() if v is not None}
    if not values:
        raise HTTPException(status_code=400, detail="No fields to update")
    q = rooms_table.update().where(rooms_table.c.id == room_id).values(**values)
    await database.execute(q)
    return {"status": "ok"}

@router.delete("/{room_id}")
async def delete_room(room_id: str):
    await database.execute(rooms_table.delete().where(rooms_table.c.id == room_id))
    return {"status": "deleted"}
