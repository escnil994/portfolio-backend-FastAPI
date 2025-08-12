from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services import user_service, email_service
from app.core import security, config
from app.schemas import token_schemas, user_schemas

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/token", response_model=token_schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = user_service.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified. Please check your inbox for the verification link.",
        )
    access_token = security.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/suggest-username", response_model=user_schemas.SuggestUsernameResponse)
def suggest_username(
    request: user_schemas.SuggestUsernameRequest,
    db: Session = Depends(get_db)
):
    """Generates and returns available username suggestions."""
    suggestions = user_service.generate_username_suggestions(db, request.email)
    return {"suggestions": suggestions}

@router.post("/register", response_model=user_schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: user_schemas.UserRegister,
    db: Session = Depends(get_db)
):
    """Handles new user registration."""
    # Check if user with that email already exists
    if user_service.get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    # Check if username is already taken
    if user_service.get_user_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken. Please choose another one.",
        )

    # Create user in the database
    user = user_service.create_user(db, user_in)

    # Generate verification token and URL
    token = security.create_verification_token(email=user.email)
    verification_url = f"{config.settings.API_URL}/auth/verify-email?token={token}"

    # Send verification email (mocked)
    email_service.send_verification_email(
        email_to=user.email,
        username=user.username,
        verification_url=verification_url
    )

    return user

@router.get("/verify-email", response_class=HTMLResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    """Handles the email verification link click."""
    email = security.verify_verification_token(token)
    if not email:
        return HTMLResponse(content="<h1>Error</h1><p>El enlace de verificación es inválido o ha expirado.</p>", status_code=400)

    user = user_service.verify_user_email(db, email)
    if not user:
        return HTMLResponse(content="<h1>Error</h1><p>Usuario no encontrado.</p>", status_code=404)
    
    return HTMLResponse(content="<h1>¡Cuenta Verificada!</h1><p>Gracias por verificar tu correo. Ahora puedes iniciar sesión.</p>")
