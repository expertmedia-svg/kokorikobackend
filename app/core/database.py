import motor.motor_asyncio
from beanie import init_beanie
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "kokoriko_db")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

async def connect_db():
    from app.models.user import User
    from app.models.farm import Farm
    from app.models.flock import Flock
    from app.models.egg_production import EggProduction
    from app.models.health_case import HealthCase
    from app.models.ai_diagnostic import AIDiagnostic
    from app.models.calendar_event import CalendarEvent
    from app.models.other_models import (
        FeedingRecord,
        IoTReading,
        Expense,
        Sale,
        Notification,
        DiseaseKnowledge,
    )

    await init_beanie(
        database=database,
        document_models=[
            User, Farm, Flock, EggProduction, HealthCase,
            AIDiagnostic, CalendarEvent, FeedingRecord, IoTReading,
            Expense, Sale, Notification, DiseaseKnowledge
        ]
    )
    print("[OK] Connexion MongoDB etablie - KOKORIKO IA")

async def disconnect_db():
    client.close()
    print("[CLOSE] Connexion MongoDB fermee")
