"""
database.py
-----------
Connexion à la base via SQLAlchemy.

- `engine`      : le moteur de connexion (lit DATABASE_URL).
- `SessionLocal`: fabrique de sessions (une session = une conversation avec la DB).
- `Base`        : classe mère dont héritent tous les modèles (tables).
- `get_db`      : dépendance FastAPI qui fournit une session puis la referme.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de connexion. Par défaut SQLite local ; surchargée par .env (DATABASE_URL).
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./cinema.db")

# `check_same_thread` n'est nécessaire que pour SQLite (limitation de SQLite + FastAPI).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dépendance FastAPI : ouvre une session, la cède, la referme à la fin."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
