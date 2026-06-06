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
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.film import Film
from app.models.user_film import UserFilm
from app.schemas.film import FilmDetail
from app.services import tmdb
from datetime import datetime, timezone

router = APIRouter(prefix="/import", tags=["Import TMDb"])


@router.get("/decouvrir")
def decouvrir(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    annee: int | None = Query(None, description="Filtrer par année de sortie"),
    pays: str | None = Query(None, description="Code pays ISO (FR, US, JP…)"),
    page: int = Query(1, ge=1, le=500),
):
    """Renvoie une fournée de films à proposer, en SAUTANT ceux que
    l'utilisateur a déjà traités. Si aucune année n'est imposée, chaque appel
    au service pioche une année différente (1960–2026) pour varier les époques.
    On répète jusqu'à obtenir assez de nouveautés (au plus 6 essais).
    """
    deja = {
        row[0]
        for row in db.query(Film.tmdb_id)
        .join(UserFilm, UserFilm.film_id == Film.id)
        .filter(UserFilm.user_id == user.id)
        .all()
    }

    try:
        a_proposer = []
        for _ in range(6):
            res = tmdb.decouvrir(page=page, annee=annee, pays=pays)
            a_proposer.extend(f for f in res["films"] if f["tmdb_id"] not in deja)
            if len(a_proposer) >= 10:
                break
        return {"films": a_proposer, "page_suivante": page + 1, "total_pages": res["total_pages"]}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except requests.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Erreur TMDb : {e}")


@router.post("/statut/{tmdb_id}")
def importer_et_marquer(
    tmdb_id: int,
    background: BackgroundTasks,
    vu: bool = Query(...),
    note: float | None = Query(None, ge=0, le=10),
    titre: str | None = Query(None),
    annee: int | None = Query(None),
    affiche: str | None = Query(None),
    note_public: float | None = Query(None),
    resume: str | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enregistre INSTANTANÉMENT le statut de l'utilisateur sur un film.

    - crée un film minimal à partir des infos déjà connues (aucun appel TMDb),
    - enregistre le statut perso (vu/pas vu, note),
    - planifie l'enrichissement complet (acteurs, genres, résumé) en tâche de
      fond, pour ne pas faire attendre l'utilisateur.
    """
    try:
        film = tmdb.creer_film_minimal(
            db, tmdb_id, titre=titre, annee=annee,
            affiche=affiche, note_public=note_public, resume=resume,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    uf = (
        db.query(UserFilm)
        .filter(UserFilm.user_id == user.id, UserFilm.film_id == film.id)
        .first()
    )
    if uf is None:
        uf = UserFilm(user_id=user.id, film_id=film.id)
        db.add(uf)
    uf.vu = vu
    if vu and uf.vu_le is None:
        uf.vu_le = datetime.now(timezone.utc)
    if note is not None:
        uf.note = note
    db.commit()

    # Enrichissement différé (ne bloque pas la réponse).
    background.add_task(tmdb.enrichir_film, tmdb_id)

    return {"film_id": film.id, "titre": film.titre_francais, "vu": vu, "note": note}


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
