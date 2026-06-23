"""Database engine + session. DB_URL swaps SQLite <-> Postgres in one line."""
import os
from sqlmodel import SQLModel, Session, create_engine

from app.core.config import settings

# Ensure the SQLite data dir exists for the zero-setup local default.
if settings.db_url.startswith("sqlite"):
    os.makedirs(settings.data_dir, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.db_url.startswith("sqlite") else {}
engine = create_engine(settings.db_url, echo=False, connect_args=connect_args)


def init_db() -> None:
    # Import models so SQLModel registers the tables before create_all.
    import app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
