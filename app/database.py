from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa para os modelos ORM (definidos na Fase 1)."""


def get_db():
    """Dependência FastAPI: abre uma sessão por request e fecha ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
