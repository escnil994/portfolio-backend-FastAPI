import asyncio
from logging.config import fileConfig
import sys
import os

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. Agregar path para ver la app
sys.path.append(os.getcwd())

# 2. Importar configuración y modelos
from app.config import settings
from app.db.base import Base

# Importar modelos para que Alembic detecte cambios
from app.models.user import User
from app.models.profile import Profile
from app.models.project import Project
from app.models.blog import BlogPost
from app.models.comment import Comment
from app.models.media import Image, Video
from app.models.contact import ContactMessage
from app.models.reaction import Reaction
from app.models.subscriber import Subscriber

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL  # Usar URL directa de settings
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    # 1. Leer la sección de configuración
    configuration = config.get_section(config.config_ini_section) or {}
    
    # 2. <--- FIX: FORZAR LA URL DESDE SETTINGS AQUÍ --->
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,  # Pasamos el diccionario modificado
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())