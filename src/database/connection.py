"""
Configuração de conexão com PostgreSQL - BullBot Telegram
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.utils.config import settings


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Engine do SQLAlchemy - Set to True for SQL debugging
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Criar todas as tabelas"""
    Base.metadata.create_all(bind=engine)
