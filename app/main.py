# Main application entry point.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.routers import auth_router


# This command creates the database tables if they don't exist.
# You might want to use a migration tool like Alembic for production.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    # Add other metadata as needed
)

# --- CORS Middleware ---
# This allows your Angular frontend to communicate with the backend.
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- API Routers ---
# Include the authentication router.
app.include_router(auth_router.router)

# Include other routers here once they are created.
# app.include_router(profile_router.router)
# app.include_router(projects_router.router)
# app.include_router(interactions_router.router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}