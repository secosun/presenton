from contextlib import asynccontextmanager
import os

from fastapi import FastAPI

from migrations import migrate_database_on_startup
from services.database import create_db_and_tables
from utils.get_env import get_app_data_directory_env
@asynccontextmanager
async def app_lifespan(_: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Initializes the application data directory, runs Alembic migrations when
    MIGRATE_DATABASE_ON_STARTUP=true, and creates any missing tables.
    LLM/image provider startup checks are skipped (materialize-only API surface).
    """
    os.makedirs(get_app_data_directory_env(), exist_ok=True)
    await migrate_database_on_startup()
    await create_db_and_tables()
    yield
