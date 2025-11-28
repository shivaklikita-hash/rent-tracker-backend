from fastapi import APIRouter, HTTPException
from database import database, rooms
import uuid
from pydantic import BaseModel

router = APIRouter()

class RoomIn(BaseModel):
    floor_id: str
    room_number: str
    tenant_name: str = None
    rent_amount: float = 0
    advance_amount: float = 0

@router.post('/')
async def create_room(r: RoomIn):
    rid = str(uuid.uuid4())
    await database.execute(rooms.insert().values(
        id=rid, floor_id=r.floor_id, room_number=r.room_number,
        tenant_name=r.tenant_name, rent_amount=r.rent_amount, advance_amount=r.advance_amount
    ))
    return {'id': rid}

@router.get('/')
async def list_rooms(floor_id: str = None):
    q = rooms.select()
    if floor_id:
        q = q.where(rooms.c.floor_id == floor_id)
    res = await database.fetch_all(q)
    out = []
    for r in res:
        item = dict(r)
        item['last_status'] = 'pending'
        out.append(item)
    return out

@router.get('/{room_id}')
async def get_room(room_id: str):
    q = rooms.select().where(rooms.c.id == room_id)
    r = await database.fetch_one(q)
    if not r:
        raise HTTPException(status_code=404)
    return r
