import os
import databases
import sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Numeric, Text, TIMESTAMP, ForeignKey, MetaData

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise Exception('DATABASE_URL environment variable is required')

database = databases.Database(DATABASE_URL)
metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', String, primary_key=True),
    Column('name', String),
    Column('email', String, unique=True),
    Column('password_hash', String),
    Column('created_at', TIMESTAMP)
)

buildings = Table(
    'buildings', metadata,
    Column('id', String, primary_key=True),
    Column('user_id', String, ForeignKey('users.id')),
    Column('name', String),
    Column('created_at', TIMESTAMP)
)

floors = Table(
    'floors', metadata,
    Column('id', String, primary_key=True),
    Column('building_id', String, ForeignKey('buildings.id')),
    Column('floor_number', Integer),
    Column('created_at', TIMESTAMP)
)

rooms = Table(
    'rooms', metadata,
    Column('id', String, primary_key=True),
    Column('floor_id', String, ForeignKey('floors.id')),
    Column('room_number', String),
    Column('tenant_name', String),
    Column('rent_amount', Numeric, default=0),
    Column('advance_amount', Numeric, default=0),
    Column('created_at', TIMESTAMP)
)

payments = Table(
    'payments', metadata,
    Column('id', String, primary_key=True),
    Column('room_id', String, ForeignKey('rooms.id')),
    Column('month', Integer),
    Column('year', Integer),
    Column('status', String),
    Column('amount_collected', Numeric, default=0),
    Column('advance_used', Numeric, default=0),
    Column('note', Text),
    Column('created_at', TIMESTAMP)
)
