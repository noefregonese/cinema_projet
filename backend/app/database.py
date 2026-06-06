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

# Certains hébergeurs (dont Neon) fournissent une URL en "postgres://" alors que
# SQLAlchemy attend "postgresql://". On normalise pour éviter une erreur.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

est_sqlite = DATABASE_URL.startswith("sqlite")

# `check_same_thread` n'est nécessaire que pour SQLite (limitation SQLite + FastAPI).
connect_args = {"check_same_thread": False} if est_sqlite else {}

# pool_pre_ping : vérifie que la connexion est vivante avant de l'utiliser.
# Indispensable avec une base distante (Neon) qui peut couper les connexions
# inactives — évite les erreurs après une période de veille.
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=not est_sqlite,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dépendance FastAPI : ouvre une session, la cède, la referme à la fin."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
