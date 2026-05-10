"""
Script de données de test pour KOKORIKO IA.
Usage: python seed_data.py
"""
import asyncio
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def seed():
    from app.core.database import connect_db
    from app.models.user import User, UserRole, ExperienceLevel
    from app.models.farm import Farm
    from app.models.flock import Flock, FlockStatus
    from app.models.egg_production import EggProduction
    from app.models.health_case import HealthCase, GravityLevel
    from app.models.other_models import Expense, Sale, DiseaseKnowledge, Notification
    from app.models.calendar_event import CalendarEvent
    from app.core.security import hash_password
    
    await connect_db()
    print("[START] Debut du peuplement de donnees KOKORIKO IA...")
    
    # Admin
    admin = await User.find_one(User.email == "admin@kokoriko.bf")
    if not admin:
        admin = User(
            nom="Administrateur",
            prenom="KOKORIKO",
            email="admin@kokoriko.bf",
            telephone="+22670000000",
            password_hash=hash_password("Admin@2024"),
            role=UserRole.admin,
            village="Ouagadougou",
            pays="Burkina Faso"
        )
        await admin.insert()
        print("[OK] Admin cree: admin@kokoriko.bf / Admin@2024")
    
    # Éleveur test
    eleveur = await User.find_one(User.telephone == "+22676543210")
    if not eleveur:
        eleveur = User(
            nom="Ouédraogo",
            prenom="Ibrahima",
            email="ibrahima@test.bf",
            telephone="+22676543210",
            password_hash=hash_password("Test@1234"),
            role=UserRole.eleveur,
            village="Koudougou",
            pays="Burkina Faso",
            niveau_experience=ExperienceLevel.intermediaire,
            taille_elevage=500
        )
        await eleveur.insert()
        print("[OK] Eleveur cree: +22676543210 / Test@1234")
    
    # Élevage
    farm = await Farm.find_one(Farm.user_id == str(eleveur.id))
    if not farm:
        farm = Farm(
            user_id=str(eleveur.id),
            nom="Poulailler Étoile du Mogho",
            localisation="Route de Bobo, km 5",
            village="Koudougou",
            pays="Burkina Faso",
            capacite_totale=600,
            temperature_cible=22.0,
            description="Élevage de poules pondeuses, spécialité ISA Brown"
        )
        await farm.insert()
        print("[OK] Elevage cree")
    
    # Lot principal
    flock = await Flock.find_one(Flock.farm_id == str(farm.id))
    if not flock:
        flock = Flock(
            farm_id=str(farm.id),
            user_id=str(eleveur.id),
            nom="Lot A - ISA Brown",
            race="ISA Brown",
            nombre_poules=300,
            age_semaines=28,
            date_arrivee=datetime.utcnow() - timedelta(weeks=28),
            fournisseur="FASO AVICULTURE",
            statut=FlockStatus.actif,
            prix_achat_unitaire=3500
        )
        await flock.insert()
        print("[OK] Lot cree: 300 ISA Brown")
    
    # Productions des 14 derniers jours
    for i in range(14):
        jour = datetime.utcnow() - timedelta(days=i)
        oeufs = 250 + (i % 3) * 5 - (i % 7) * 2  # variation réaliste
        prod_exists = await EggProduction.find_one(
            EggProduction.flock_id == str(flock.id),
            EggProduction.date >= jour.replace(hour=0, minute=0),
            EggProduction.date < jour.replace(hour=23, minute=59)
        )
        if not prod_exists:
            prod = EggProduction(
                flock_id=str(flock.id),
                farm_id=str(farm.id),
                user_id=str(eleveur.id),
                date=jour,
                oeufs_collectes=oeufs,
                oeufs_casses=int(oeufs * 0.02),
                oeufs_vendus=int(oeufs * 0.8),
                oeufs_consommes=2,
                stock_restant=int(oeufs * 0.18),
                prix_vente_unitaire=150,
                taux_ponte=round(oeufs / 300 * 100, 1),
                revenu_jour=int(oeufs * 0.8) * 150
            )
            await prod.insert()
    print("[OK] 14 jours de production crees")
    
    # Cas de santé
    case = await HealthCase.find_one(HealthCase.farm_id == str(farm.id))
    if not case:
        case = HealthCase(
            flock_id=str(flock.id),
            farm_id=str(farm.id),
            user_id=str(eleveur.id),
            date=datetime.utcnow() - timedelta(days=3),
            symptomes=["plumes ébouriffées", "diminution de l'appétit", "diarrhée légère"],
            description="Quelques poules présentent des signes de fatigue et moins mangent",
            nombre_poules_touchees=12,
            mortalite=0,
            gravite=GravityLevel.moyen,
            traitement_donne="Vitamines dans l'eau + isolation des poules malades"
        )
        await case.insert()
        print("[OK] Cas sanitaire de test cree")
    
    # Dépenses
    depense = await Expense.find_one(Expense.farm_id == str(farm.id))
    if not depense:
        depenses_data = [
            ("alimentation", "Achat aliment complet pondeuses 500kg", 75000),
            ("medicament", "Vitamines et électrolytes", 15000),
            ("eau_electricite", "Facture eau juillet", 8500),
            ("materiel", "Réparation abreuvoir", 5000),
        ]
        for type_d, desc, montant in depenses_data:
            d = Expense(
                user_id=str(eleveur.id),
                farm_id=str(farm.id),
                type_depense=type_d,
                description=desc,
                montant_fcfa=montant,
                date=datetime.utcnow() - timedelta(days=5)
            )
            await d.insert()
        print("[OK] Depenses de test creees")
    
    # Base de connaissances maladies
    disease_count = await DiseaseKnowledge.count()
    if disease_count == 0:
        maladies = [
            {
                "nom": "Newcastle",
                "nom_local": "Maladie de la tête",
                "symptomes": ["torsion du cou", "paralysie", "écoulement nasal", "chute brutale de ponte"],
                "causes": ["Virus paramyxovirus", "Contact avec oiseaux sauvages", "Mauvaise biosécurité"],
                "traitement_general": "Aucun traitement curatif. Vaccination préventive obligatoire.",
                "prevention": "Vaccination régulière, biosécurité stricte, éviter les oiseaux sauvages",
                "gravite": "urgent",
                "necessite_veterinaire": True,
                "region_frequente": "Afrique de l'Ouest",
                "saison": "Toutes saisons"
            },
            {
                "nom": "Coccidiose",
                "nom_local": "Maladie du sang dans les fientes",
                "symptomes": ["fientes sanguinolentes", "amaigrissement", "plumes ébouriffées", "mort subite"],
                "causes": ["Parasites Eimeria", "Litière humide", "Densité élevée"],
                "traitement_general": "Anticoccidiens dans l'eau. Améliorer la ventilation et sécher la litière.",
                "prevention": "Litière sèche, densité normale, anticoccidiens préventifs",
                "gravite": "moyen",
                "necessite_veterinaire": True,
                "region_frequente": "Afrique subsaharienne",
                "saison": "Saison des pluies"
            },
            {
                "nom": "Marek",
                "nom_local": "Paralysie des pattes",
                "symptomes": ["paralysie d'une patte ou aile", "amaigrissement progressif", "œil gris"],
                "causes": ["Herpèsvirus de la volaille", "Très contagieux"],
                "traitement_general": "Pas de traitement. Vaccination des poussins à 1 jour.",
                "prevention": "Vaccination à l'éclosion obligatoire",
                "gravite": "urgent",
                "necessite_veterinaire": True
            }
        ]
        for m in maladies:
            d = DiseaseKnowledge(**m)
            await d.insert()
        print("[OK] Base de connaissances maladies creee")
    
    # Événements calendrier
    event_count = await CalendarEvent.count()
    if event_count == 0:
        from app.models.calendar_event import EventType
        evenements = [
            ("Vaccination Newcastle", EventType.vaccination, 7),
            ("Nettoyage complet poulailler", EventType.nettoyage, 3),
            ("Désinfection eau", EventType.desinfection, 5),
            ("Achat aliment - réappro", EventType.alimentation, 10),
            ("Visite vétérinaire annuelle", EventType.veterinaire, 30),
        ]
        for titre, type_ev, jours in evenements:
            ev = CalendarEvent(
                user_id=str(eleveur.id),
                farm_id=str(farm.id),
                titre=titre,
                type_evenement=type_ev,
                date_prevue=datetime.utcnow() + timedelta(days=jours),
                rappel_active=True
            )
            await ev.insert()
        print("[OK] Evenements calendrier crees")
    
    print("\n[SUCCESS] Donnees de test KOKORIKO IA peuplees avec succes!")
    print("\n[ACCOUNTS] COMPTES DE TEST:")
    print("   Admin:   admin@kokoriko.bf / Admin@2024")
    print("   Eleveur: +22676543210 / Test@1234")
    print("\n[INFO] Demarrez le serveur: uvicorn app.main:app --reload")

if __name__ == "__main__":
    asyncio.run(seed())
