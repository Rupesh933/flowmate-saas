# to connect Database to FastAPI
'''
1. Creating a connection to PostgeSQL (Engine)
2. Providing a 'session' for each request (like a conversation with the database)
3. All models (USER, TASKS) is inherit from Base class
'''

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# load the .env file
load_dotenv()

# Take DATABASE_URL from .env  ( DATABASE_URL=postgresql://rupesh_admin:Rupesh2026@db:5432/flowmate_saas )
DATABASE_URL = os.getenv("DATABASE_URL")

# Create Engine - this is actul connection from PostgeSQL
engine = create_engine(DATABASE_URL)

# SessionLocal - for every request has new conversition
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Class - every table (models) inherit from this
class Base(DeclarativeBase):
    pass

# Dependency - FastAPI is use this and give DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()