# tests/unit/test_auth_service.py

import pytest
from app.services.auth import auth_service


class TestAuthService:
    
    def test_password_hashing(self):
        password = "testpassword123"
        hashed = auth_service.get_password_hash(password)
        
        assert hashed != password
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrongpassword", hashed)
    
    def test_create_access_token(self):
        data = {"user_id": 1, "email": "test@example.com"}
        token = auth_service.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["email"] == "test@example.com"
    
    def test_verify_invalid_token(self):
        payload = auth_service.verify_token("invalid_token")
        assert payload is None
    
    def test_generate_2fa_code(self):
        code = auth_service.generate_2fa_code()
        
        assert len(code) == 6
        assert code.isdigit()
    
    def test_generate_totp_secret(self):
        secret = auth_service.generate_totp_secret()
        
        assert secret is not None
        assert len(secret) == 32
    
    def test_verify_totp(self):
        secret = auth_service.generate_totp_secret()
        
        import pyotp
        totp = pyotp.TOTP(secret)
        code = totp.now()
        
        assert auth_service.verify_totp(secret, code)
    
    def test_generate_backup_codes(self):
        codes = auth_service.generate_backup_codes(count=5)
        
        assert len(codes) == 5
        for code in codes:
            assert len(code) == 9
            assert "-" in code
    
    def test_backup_code_hashing(self):
        codes = ["ABCD-1234", "EFGH-5678"]
        hashed = auth_service.hash_backup_codes(codes)
        
        assert hashed is not None
        assert "|" in hashed
        assert auth_service.verify_backup_code(hashed, "ABCD-1234")
        assert auth_service.verify_backup_code(hashed, "EFGH-5678")
        assert not auth_service.verify_backup_code(hashed, "WRONG-CODE")


class TestAuthServiceDatabase:
    
    @pytest.mark.asyncio
    async def test_create_user(self, test_db):
        user = await auth_service.create_user(
            db=test_db,
            email="newuser@example.com",
            username="newuser",
            password="password123",
            full_name="New User",
            is_superuser=False
        )
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.full_name == "New User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.hashed_password != "password123"
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, test_db, test_user):
        user = await auth_service.get_user_by_email(test_db, test_user.email)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_db, test_user):
        user = await auth_service.get_user_by_id(test_db, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, test_db, test_user):
        user = await auth_service.authenticate_user(
            test_db,
            test_user.email,
            "testpassword123"
        )
        
        assert user is not None
        assert user.id == test_user.id
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, test_db, test_user):
        user = await auth_service.authenticate_user(
            test_db,
            test_user.email,
            "wrongpassword"
        )
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_email(self, test_db):
        user = await auth_service.authenticate_user(
            test_db,
            "nonexistent@example.com",
            "password123"
        )
        
        assert user is None