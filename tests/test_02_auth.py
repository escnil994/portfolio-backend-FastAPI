import pytest
import uuid
from app.services.auth import auth_service

@pytest.mark.asyncio
async def test_login_con_usuario_inyectado(client, db):
    # 1. PREPARACIÓN: Datos aleatorios para no repetir emails
    random_id = str(uuid.uuid4())[:8]
    password_raw = "TestPass123!"
    email_test = f"test_{random_id}@internal.com"
    username_test = f"user_{random_id}"
    
    # 2. INYECCIÓN: Crear usuario "por detrás" (directo en DB)
    # Usamos el servicio interno para que hashee la contraseña correctamente
    try:
        await auth_service.create_user(
            db=db, 
            email=email_test,
            username=username_test,
            password=password_raw,
            full_name="Internal Test User",
            is_superuser=False
        )
        print(f"\n✅ Usuario inyectado en DB: {email_test}")
    except Exception as e:
        pytest.fail(f"No se pudo crear el usuario en DB: {e}")

    # 3. ACCIÓN: Intentar Login por la API
    # Usamos 'identifier' como descubrimos en el error anterior
    credenciales = {
        "identifier": email_test,
        "password": password_raw
    }
    
    response = await client.post("/api/v1/auth/login", json=credenciales)

    # 4. VERIFICACIÓN
    if response.status_code != 200:
        print(f"⚠️ Error API: {response.json()}")

    assert response.status_code == 200
    token = response.json()
    assert "access_token" in token
    print("✅ Login exitoso. Token recibido.")