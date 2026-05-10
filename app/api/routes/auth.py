from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

class RegisterRequest(BaseModel):
    nom: str
    prenom: str
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    password: str
    village: Optional[str] = None
    pays: str = "Burkina Faso"
    langue: str = "fr"

class LoginRequest(BaseModel):
    identifiant: str  # email ou telephone
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    nom: str
    role: str

@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest):
    # Vérifier si email/tel déjà utilisé
    if data.email:
        existing = await User.find_one(User.email == data.email)
        if existing:
            raise HTTPException(400, "Email déjà utilisé")
    if data.telephone:
        existing = await User.find_one(User.telephone == data.telephone)
        if existing:
            raise HTTPException(400, "Téléphone déjà utilisé")
    
    if not data.email and not data.telephone:
        raise HTTPException(400, "Email ou téléphone requis")
    
    user = User(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        telephone=data.telephone,
        password_hash=hash_password(data.password),
        village=data.village,
        pays=data.pays,
        langue=data.langue,
        role=UserRole.eleveur
    )
    await user.insert()
    
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        nom=f"{user.prenom} {user.nom}",
        role=user.role
    )

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    # Chercher par email ou téléphone
    user = None
    if "@" in data.identifiant:
        user = await User.find_one(User.email == data.identifiant)
    else:
        user = await User.find_one(User.telephone == data.identifiant)
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Identifiant ou mot de passe incorrect")
    
    if not user.is_active:
        raise HTTPException(403, "Compte désactivé")
    
    user.last_login = datetime.utcnow()
    await user.save()
    
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        nom=f"{user.prenom} {user.nom}",
        role=user.role
    )

@router.post("/logout")
async def logout():
    return {"message": "Déconnexion réussie"}
