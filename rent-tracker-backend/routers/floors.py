from fastapi import APIRouter, HTTPException
from database import database, floors
import uuid
from pydantic import BaseModel

router = APIRouter()

class FloorIn(BaseModel):
    building_id: str
    floor_number: int

@router.post('/')
async def create_floor(f: FloorIn):
    fid = str(uuid.uuid4())
    await database.execute(floors.insert().values(id=fid, building_id=f.building_id, floor_number=f.floor_number))
    return {'id': fid, 'floor_number': f.floor_number}

@router.get('/')
async def list_floors(building_id: str = None):
    q = floors.select()
    if building_id:
        q = q.where(floors.c.building_id == building_id)
    res = await database.fetch_all(q)
    return res
