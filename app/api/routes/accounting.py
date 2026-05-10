from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from app.models.other_models import Expense, Sale, ExpenseType
from app.core.security import get_current_user

router = APIRouter()

class ExpenseCreate(BaseModel):
    type_depense: ExpenseType
    description: str
    montant_fcfa: float
    date: datetime
    farm_id: Optional[str] = None
    flock_id: Optional[str] = None
    fournisseur: Optional[str] = None
    note: Optional[str] = None

class SaleCreate(BaseModel):
    type_vente: str
    quantite: float
    prix_unitaire: float
    date: datetime
    farm_id: Optional[str] = None
    flock_id: Optional[str] = None
    acheteur: Optional[str] = None
    note: Optional[str] = None

@router.post("/expenses")
async def add_expense(data: ExpenseCreate, current_user=Depends(get_current_user)):
    expense = Expense(**data.dict(), user_id=str(current_user.id))
    await expense.insert()
    return {"id": str(expense.id), "message": "Dépense enregistrée"}

@router.get("/expenses")
async def get_expenses(farm_id: Optional[str] = None, jours: int = 30, current_user=Depends(get_current_user)):
    depuis = datetime.utcnow() - timedelta(days=jours)
    filters = [Expense.user_id == str(current_user.id), Expense.date >= depuis]
    if farm_id:
        filters.append(Expense.farm_id == farm_id)
    expenses = await Expense.find(*filters).sort("-date").to_list()
    return [{"id": str(e.id), **e.dict(exclude={"id", "revision_id"})} for e in expenses]

@router.post("/sales")
async def add_sale(data: SaleCreate, current_user=Depends(get_current_user)):
    montant_total = data.quantite * data.prix_unitaire
    sale = Sale(**data.dict(), montant_total=montant_total, user_id=str(current_user.id))
    await sale.insert()
    return {"id": str(sale.id), "message": "Vente enregistrée", "montant_total": montant_total}

@router.get("/sales")
async def get_sales(farm_id: Optional[str] = None, jours: int = 30, current_user=Depends(get_current_user)):
    depuis = datetime.utcnow() - timedelta(days=jours)
    filters = [Sale.user_id == str(current_user.id), Sale.date >= depuis]
    if farm_id:
        filters.append(Sale.farm_id == farm_id)
    sales = await Sale.find(*filters).sort("-date").to_list()
    return [{"id": str(s.id), **s.dict(exclude={"id", "revision_id"})} for s in sales]

@router.get("/summary")
async def get_summary(farm_id: Optional[str] = None, jours: int = 30, current_user=Depends(get_current_user)):
    """Résumé financier."""
    depuis = datetime.utcnow() - timedelta(days=jours)
    
    exp_filters = [Expense.user_id == str(current_user.id), Expense.date >= depuis]
    sale_filters = [Sale.user_id == str(current_user.id), Sale.date >= depuis]
    if farm_id:
        exp_filters.append(Expense.farm_id == farm_id)
        sale_filters.append(Sale.farm_id == farm_id)
    
    expenses = await Expense.find(*exp_filters).to_list()
    sales = await Sale.find(*sale_filters).to_list()
    
    total_depenses = sum(e.montant_fcfa for e in expenses)
    total_revenus = sum(s.montant_total for s in sales)
    benefice = total_revenus - total_depenses
    
    # Dépenses par catégorie
    par_categorie = {}
    for e in expenses:
        cat = e.type_depense.value
        par_categorie[cat] = par_categorie.get(cat, 0) + e.montant_fcfa
    
    return {
        "periode_jours": jours,
        "total_depenses": total_depenses,
        "total_revenus": total_revenus,
        "benefice": benefice,
        "rentabilite_pct": round((benefice / total_depenses * 100) if total_depenses > 0 else 0, 1),
        "depenses_par_categorie": par_categorie,
        "nombre_ventes": len(sales),
        "nombre_depenses": len(expenses)
    }
