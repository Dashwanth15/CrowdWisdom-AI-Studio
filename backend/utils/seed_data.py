"""
Seed data script for CrowdWisdom AI Studio development.
Creates a default admin user, sample campaign, and integration stubs.
Run: python -m utils.seed_data
"""
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def seed():
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from database.connection import connect_to_mongo, get_database
    from services.auth_service import hash_password
    from services.integration_service import initialize_default_integrations

    await connect_to_mongo()
    db = get_database()

    # Create admin user if not exists
    existing = await db.users.find_one({"email": "admin@crowdwisdom.ai"})
    if not existing:
        await db.users.insert_one({
            "email": "admin@crowdwisdom.ai",
            "username": "admin",
            "full_name": "CrowdWisdom Admin",
            "password_hash": hash_password("admin1234"),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        print("✓ Admin user created: admin@crowdwisdom.ai / admin1234")
    else:
        print("✓ Admin user already exists")

    # Initialize default integrations
    await initialize_default_integrations()
    print("✓ Default integrations initialized")

    print("\nSeeding complete! Start the backend with:")
    print("  cd backend && uvicorn main:app --reload")


if __name__ == "__main__":
    asyncio.run(seed())

