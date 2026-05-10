from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta, date

from app.models.egg_production import EggProduction
from app.models.flock import Flock
from app.models.other_models import Sale, Notification
from app.core.security import get_current_user

router = APIRouter()

class EggProductionCreate(BaseModel):
    flock_id: str
    farm_id: str
    date: str  # Accept ISO8601 string, will be parsed by FastAPI
    oeufs_collectes: int
    oeufs_casses: int = 0
    oeufs_vendus: int = 0
    oeufs_consommes: int = 0
    prix_vente_unitaire: Optional[float] = None
    observation: Optional[str] = None

@router.post("/")
async def record_production(data: EggProductionCreate, current_user=Depends(get_current_user)):
    flock = await Flock.get(data.flock_id)
    if not flock:
        raise HTTPException(404, "Lot introuvable")

    # Parse datetime from ISO8601 string
    try:
        if isinstance(data.date, str):
            prod_date = datetime.fromisoformat(data.date.replace('Z', '+00:00'))
        else:
            prod_date = data.date
    except (ValueError, AttributeError):
        raise HTTPException(400, "Format date invalide. Utilisez ISO8601.")

    # Calcul automatique
    stock_restant = data.oeufs_collectes - data.oeufs_casses - data.oeufs_vendus - data.oeufs_consommes
    taux_ponte = (data.oeufs_collectes / flock.nombre_poules * 100) if flock.nombre_poules > 0 else 0
    revenu = (data.oeufs_vendus * data.prix_vente_unitaire) if data.prix_vente_unitaire else None

    # Vérifier baisse anormale (comparer avec production moyenne des 7 derniers jours)
    semaine_passee = prod_date - timedelta(days=7)
    historique = await EggProduction.find(
        EggProduction.flock_id == data.flock_id,
        EggProduction.date >= semaine_passee,
        EggProduction.date < prod_date
    ).to_list()
    
    alerte_baisse = False
    if historique:
        moyenne = sum(p.oeufs_collectes for p in historique) / len(historique)
        if data.oeufs_collectes < moyenne * 0.80:  # baisse > 20%
            alerte_baisse = True
            # Créer notification d'alerte
            notif = Notification(
                user_id=str(current_user.id),
                titre="⚠️ Baisse de production détectée",
                message=f"La production du lot {flock.nom} a chuté de {round((1 - data.oeufs_collectes/moyenne)*100)}%. Vérifiez la santé et l'alimentation.",
                type="baisse_ponte"
            )
            await notif.insert()

    # Enregistrer vente auto si prix renseigné
    if data.oeufs_vendus > 0 and data.prix_vente_unitaire:
        vente = Sale(
            user_id=str(current_user.id),
            farm_id=data.farm_id,
            flock_id=data.flock_id,
            type_vente="oeufs",
            quantite=data.oeufs_vendus,
            prix_unitaire=data.prix_vente_unitaire,
            montant_total=data.oeufs_vendus * data.prix_vente_unitaire,
            date=prod_date
        )
        await vente.insert()

    production = EggProduction(
        flock_id=data.flock_id,
        farm_id=data.farm_id,
        user_id=str(current_user.id),
        date=prod_date,
        oeufs_collectes=data.oeufs_collectes,
        oeufs_casses=data.oeufs_casses,
        oeufs_vendus=data.oeufs_vendus,
        oeufs_consommes=data.oeufs_consommes,
        prix_vente_unitaire=data.prix_vente_unitaire,
        observation=data.observation,
        stock_restant=max(0, stock_restant),
        taux_ponte=round(taux_ponte, 1),
        revenu_jour=revenu,
        alerte_baisse=alerte_baisse
    )
    await production.insert()
    
    return {
        "id": str(production.id),
        "message": "Production enregistrée",
        "taux_ponte": round(taux_ponte, 1),
        "stock_restant": max(0, stock_restant),
        "alerte_baisse": alerte_baisse,
        "revenu_jour": revenu
    }

@router.get("/flock/{flock_id}")
async def get_productions(flock_id: str, jours: int = 30, current_user=Depends(get_current_user)):
    depuis = datetime.utcnow() - timedelta(days=jours)
    productions = await EggProduction.find(
        EggProduction.flock_id == flock_id,
        EggProduction.user_id == str(current_user.id),
        EggProduction.date >= depuis
    ).sort("-date").to_list()
    
    data = [{"id": str(p.id), **p.dict(exclude={"id", "revision_id"})} for p in productions]
    
    # Statistiques
    if productions:
        total_oeufs = sum(p.oeufs_collectes for p in productions)
        taux_moyen = sum(p.taux_ponte or 0 for p in productions) / len(productions)
        return {
            "productions": data,
            "stats": {
                "total_oeufs": total_oeufs,
                "taux_ponte_moyen": round(taux_moyen, 1),
                "production_journaliere_moyenne": round(total_oeufs / len(productions), 1),
                "nombre_jours": len(productions)
            }
        }
    return {"productions": data, "stats": {}}

@router.get("/farm/{farm_id}/today")
async def get_today_production(farm_id: str, current_user=Depends(get_current_user)):
    today = datetime.combine(date.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    
    productions = await EggProduction.find(
        EggProduction.farm_id == farm_id,
        EggProduction.date >= today,
        EggProduction.date < tomorrow
    ).to_list()
    
    return {
        "date": today.isoformat(),
        "total_oeufs": sum(p.oeufs_collectes for p in productions),
        "total_casses": sum(p.oeufs_casses for p in productions),
        "total_vendus": sum(p.oeufs_vendus for p in productions),
        "revenu_total": sum(p.revenu_jour or 0 for p in productions),
        "productions": [{"id": str(p.id), **p.dict(exclude={"id", "revision_id"})} for p in productions]
    }
