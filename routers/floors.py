from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid
from database import database, floors as floors_table, rooms as rooms_table

router = APIRouter()

class FloorCreate(BaseModel):
    building_id: str
    floor_number: int

class FloorUpdate(BaseModel):
    floor_number: int

@router.get("/")
async def list_floors(building_id: str):
    q = floors_table.select().where(floors_table.c.building_id == building_id)
    rows = await database.fetch_all(q)
    return [dict(r) for r in rows]

@router.post("/")
async def create_floor(payload: FloorCreate):
    fid = str(uuid.uuid4())
    await database.execute(floors_table.insert().values(
        id=fid, building_id=payload.building_id, floor_number=payload.floor_number
    ))
    return {"id": fid, "building_id": payload.building_id, "floor_number": payload.floor_number}

@router.put("/{floor_id}")
async def update_floor(floor_id: str, payload: FloorUpdate):
    q = floors_table.update().where(floors_table.c.id == floor_id).values(floor_number=payload.floor_number)
    await database.execute(q)
    return {"status": "ok"}

@router.delete("/{floor_id}")
async def delete_floor(floor_id: str):
    # delete rooms for the floor first
    await database.execute(rooms_table.delete().where(rooms_table.c.floor_id == floor_id))
    await database.execute(floors_table.delete().where(floors_table.c.id == floor_id))
    return {"status": "deleted"}
