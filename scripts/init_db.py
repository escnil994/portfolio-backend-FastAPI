# scripts/init_db.py

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.session import init_db, close_db


async def initialize_database():
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    print()
    
    try:
        print("Creating database tables...")
        await init_db()
        print("✅ Database tables created successfully!")
        print()
        print("Next steps:")
        print("1. Run migrations: alembic upgrade head")
        print("2. Create admin user: python scripts/create_admin.py")
        print("3. Seed sample data (optional): python scripts/seed_data.py")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(initialize_database())