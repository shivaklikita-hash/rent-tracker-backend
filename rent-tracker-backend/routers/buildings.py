from fastapi import APIRouter, HTTPException
from database import database, buildings
import uuid
from pydantic import BaseModel

router = APIRouter()

class BuildingIn(BaseModel):
    name: str
    user_id: str = None

@router.post('/', summary='Create building')
async def create_building(b: BuildingIn):
    bid = str(uuid.uuid4())
    await database.execute(buildings.insert().values(id=bid, name=b.name, user_id=b.user_id))
    return {'id': bid, 'name': b.name}

@router.get('/', summary='List buildings')
async def list_buildings(user_id: str = None):
    q = buildings.select()
    if user_id:
        q = q.where(buildings.c.user_id == user_id)
    res = await database.fetch_all(q)
    return res

@router.get('/{building_id}')
async def get_building(building_id: str):
    q = buildings.select().where(buildings.c.id == building_id)
    b = await database.fetch_one(q)
    if not b:
        raise HTTPException(status_code=404, detail='Not found')
    return b
