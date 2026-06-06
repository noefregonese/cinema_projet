"""
main.py
-------
Point d'entrée de l'application FastAPI.

  - crée les tables au démarrage (pratique en dev ; en prod on passera par
    Alembic pour gérer les migrations proprement),
  - configure CORS pour que le frontend (localhost:5173) puisse appeler l'API,
  - monte les routers (pour l'instant : authentification).

Lancer :  uvicorn app.main:app --reload
Doc interactive : http://localhost:8000/docs
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
import app.models          # enregistre tous les modèles sur Base
from app.routers import auth, films, mes_films, import_tmdb, stats

# Crée les tables manquantes au démarrage.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cinéma API", version="0.1.0")

# CORS : quelles origines (sites) ont le droit d'appeler l'API.
# En local : le frontend Vite. En prod : le domaine Vercel, fourni via la
# variable d'environnement FRONTEND_URL (ex. "https://cinema-xyz.vercel.app").
origines = ["http://localhost:5173", "http://127.0.0.1:5173"]
frontend_url = os.environ.get("FRONTEND_URL")
if frontend_url:
    origines.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origines,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(films.router)
app.include_router(mes_films.router)
app.include_router(import_tmdb.router)
app.include_router(stats.router)


@app.get("/")
def racine():
    return {"message": "API Cinéma — voir /docs pour la documentation."}
