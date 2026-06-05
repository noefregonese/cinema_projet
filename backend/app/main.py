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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
import app.models          # enregistre tous les modèles sur Base
from app.routers import auth, films, mes_films, import_tmdb

# Crée les tables manquantes au démarrage (dev).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cinéma API", version="0.1.0")

# CORS : autorise le frontend React (Vite) en développement.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(films.router)
app.include_router(mes_films.router)
app.include_router(import_tmdb.router)


@app.get("/")
def racine():
    return {"message": "API Cinéma — voir /docs pour la documentation."}
