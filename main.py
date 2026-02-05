from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth
from database import database
from routers import buildings, floors, rooms, payments

app = FastAPI(title='Rent Tracker API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(buildings.router, prefix='/buildings', tags=['buildings'])
app.include_router(floors.router, prefix='/floors', tags=['floors'])
app.include_router(rooms.router, prefix='/rooms', tags=['rooms'])
app.include_router(payments.router, prefix='/payments', tags=['payments'])

@app.on_event("startup")
async def startup():
    try:
        await database.connect()
        print("✅ DB connected")
    except Exception as e:
        print("⚠️ DB connection failed — starting without DB:", e)

@app.on_event("shutdown")
async def shutdown():
    try:
        await database.disconnect()
    except Exception:
        pass


@app.get('/')
async def root():
    return {'status':'ok'}
