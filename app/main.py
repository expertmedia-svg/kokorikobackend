from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.database import connect_db, disconnect_db
from app.api.routes import (
    auth, users, farms, flocks, egg_production,
    health_cases, ai_diagnostic, calendar, feeding,
    iot, accounting, admin, notifications
)

app = FastAPI(
    title="KOKORIKO IA API",
    description="API backend pour l'application KOKORIKO - Gestion intelligente des élevages avicoles africains",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(users.router, prefix="/api/users", tags=["Utilisateurs"])
app.include_router(farms.router, prefix="/api/farms", tags=["Élevages"])
app.include_router(flocks.router, prefix="/api/flocks", tags=["Lots de poules"])
app.include_router(egg_production.router, prefix="/api/eggs", tags=["Production d'œufs"])
app.include_router(health_cases.router, prefix="/api/health", tags=["Santé & Maladies"])
app.include_router(ai_diagnostic.router, prefix="/api/ai", tags=["Diagnostic IA"])
app.include_router(calendar.router, prefix="/api/calendar", tags=["Calendrier avicole"])
app.include_router(feeding.router, prefix="/api/feeding", tags=["Alimentation"])
app.include_router(iot.router, prefix="/api/iot", tags=["IoT Poulailler"])
app.include_router(accounting.router, prefix="/api/accounting", tags=["Comptabilité"])
app.include_router(admin.router, prefix="/api/admin", tags=["Administration"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])

@app.get("/")
async def root():
    return {"message": "🐔 KOKORIKO IA API - Bienvenue", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": "KOKORIKO IA"}
