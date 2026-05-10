import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def create_users():
    from app.core.database import connect_db
    from app.models.user import User, UserRole
    import hashlib

    await connect_db()
    print("[START] Creating test users...")

    # Create admin user
    admin = User(
        nom="KOKORIKO",
        prenom="Administrateur",
        email="admin@kokoriko.bf",
        telephone="+22670000000",
        password_hash=hashlib.sha256("Admin@2024".encode()).hexdigest(),
        village="Ouagadougou",
        pays="Burkina Faso",
        langue="fr",
        role=UserRole.admin,
        is_active=True
    )
    await admin.insert()
    print(f"[OK] Admin created: admin@kokoriko.bf / Admin@2024")

    # Create test user (eleveur)
    user = User(
        nom="Ouédraogo",
        prenom="Ibrahima",
        email=None,
        telephone="+22676543210",
        password_hash=hashlib.sha256("Test@1234".encode()).hexdigest(),
        village="Koudougou",
        pays="Burkina Faso",
        langue="fr",
        role=UserRole.eleveur,
        is_active=True
    )
    await user.insert()
    print(f"[OK] Eleveur created: +22676543210 / Test@1234")

    print("[SUCCESS] All test users created!")

if __name__ == "__main__":
    asyncio.run(create_users())
