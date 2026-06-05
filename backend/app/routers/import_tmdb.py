"""
routers/import_tmdb.py
----------------------
Endpoints pour alimenter le catalogue depuis TMDb, directement via l'API
(remplace l'usage du terminal). Protégés : il faut être connecté.

  GET  /import/recherche?q=...        → cherche des films sur TMDb (autocomplétion)
  POST /import/film/{tmdb_id}         → importe un film TMDb dans le catalogue

Après import, l'utilisateur peut marquer le film vu / le noter via /me/films
(déjà construit à l'étape 3).
"""

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.film import FilmDetail
from app.services import tmdb

router = APIRouter(prefix="/import", tags=["Import TMDb"])


@router.get("/recherche")
def recherche_tmdb(
    q: str = Query(..., min_length=1, description="Titre à chercher sur TMDb"),
    user: User = Depends(get_current_user),
):
    """Cherche des films sur TMDb (sans rien écrire en base).
    Sert à l'utilisateur pour trouver le bon film avant de l'importer."""
    try:
        return tmdb.rechercher(q)
    except RuntimeError as e:           # clé API absente
        raise HTTPException(status_code=503, detail=str(e))
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Erreur TMDb : {e}")


@router.post("/film/{tmdb_id}", response_model=FilmDetail, status_code=201)
def importer(
    tmdb_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Importe un film TMDb dans le catalogue partagé.
    Si le film existe déjà, le renvoie sans le recréer (200/201 selon le cas)."""
    try:
        film = tmdb.importer_film(db, tmdb_id)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Erreur TMDb : {e}")
    return film
