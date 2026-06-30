from fastapi import FastAPI
from core.database import engine, Base
from modules.auth.models import User
from modules.auth.schemas import UserCreate, UserResponse

app = FastAPI(
    title="FlowMate SaaS API",
    version="1.0.0",
    description="Productivity SaaS backend"
)

# create all table which is inherit from Base
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "ok", "message": "FlowMate API is running 🚀"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/db_check")
def check_database():
    try:
        connection = engine.connect()
        connection.close()
        return {
            "database": "Connection successfully connect!"
        }
    except Exception as e:
        return {
            'datbase': "connection failed"
        }