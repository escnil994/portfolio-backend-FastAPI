# scripts/create_admin.py

import asyncio
import sys
from pathlib import Path
from getpass import getpass

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.services.auth import auth_service
from app.config import settings


async def user_exists(db, email: str) -> bool:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none() is not None


async def create_admin_user():
    print("=" * 60)
    print("Portfolio Backend - Admin User Creation")
    print("=" * 60)
    print()
    
    async with AsyncSessionLocal() as db:
        admin_email = settings.ADMIN_EMAIL
        admin_password = None
        admin_username = settings.ADMIN_USERNAME
        
        if await user_exists(db, admin_email):
            print(f"⚠️  Admin user with email '{admin_email}' already exists!")
            response = input("Do you want to update the password? (y/N): ").strip().lower()
            
            if response == 'y':
                admin_password = getpass("Enter new password: ").strip()
                confirm_password = getpass("Confirm new password: ").strip()
                
                if admin_password != confirm_password:
                    print("❌ Passwords don't match!")
                    return
                
                user = await auth_service.get_user_by_email(db, admin_email)
                user.hashed_password = auth_service.get_password_hash(admin_password)
                await db.commit()
                
                print(f"\n✅ Password updated for admin user: {admin_email}")
            else:
                print("Operation cancelled.")
            return
        
        if not hasattr(settings, 'ADMIN_PASSWORD') or not settings.ADMIN_PASSWORD:
            print("Enter admin credentials:")
            admin_email = input(f"Email [{admin_email}]: ").strip() or admin_email
            admin_username = input(f"Username [{admin_username}]: ").strip() or admin_username
            
            admin_password = getpass("Password: ").strip()
            confirm_password = getpass("Confirm Password: ").strip()
            
            if admin_password != confirm_password:
                print("❌ Passwords don't match!")
                return
        else:
            admin_password = settings.ADMIN_PASSWORD
            print(f"📧 Email: {admin_email}")
            print(f"👤 Username: {admin_username}")
            print("🔑 Password: (from environment)")
        
        if len(admin_password) < 8:
            print("❌ Password must be at least 8 characters long!")
            return
        
        print("\n⏳ Creating admin user...")
        
        try:
            admin_user = await auth_service.create_user(
                db=db,
                email=admin_email,
                username=admin_username,
                password=admin_password,
                full_name="Administrator",
                is_superuser=True
            )
            
            print("\n" + "=" * 60)
            print("✅ Admin User Created Successfully!")
            print("=" * 60)
            print(f"📧 Email: {admin_user.email}")
            print(f"👤 Username: {admin_user.username}")
            print(f"🔐 Superuser: Yes")
            print(f"✉️  2FA Enabled: Yes")
            print("=" * 60)
            print("\n⚠️  IMPORTANT: Save these credentials securely!")
            print("\n📖 Next steps:")
            print("   1. Start the API server")
            print("   2. Login at /api/v1/auth/login")
            print("   3. Check your email for 2FA code")
            print("   4. Verify with code at /api/v1/auth/verify-2fa")
            print()
            
        except Exception as e:
            print(f"\n❌ Error creating admin user: {e}")
            await db.rollback()
            raise


async def main():
    try:
        await create_admin_user()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())