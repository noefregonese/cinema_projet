"""
routers/films.py
----------------
Le CATALOGUE partagé, en lecture seule pour tout le monde.

  GET /films          → liste paginée, avec filtres (genre, année, recherche)
  GET /films/{id}     → fiche détaillée d'un film

Pas besoin d'être connecté : ces données sont les mêmes pour tous.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.film import Film
from app.models.vocab import Genre
from app.schemas.film import FilmResume, FilmDetail

router = APIRouter(prefix="/films", tags=["Catalogue"])


@router.get("", response_model=list[FilmResume])
def lister_films(
    db: Session = Depends(get_db),
    recherche: str | None = Query(None, description="Cherche dans les titres"),
    genre: str | None = Query(None, description="Nom exact d'un genre"),
    annee: int | None = Query(None, description="Année de sortie"),
    skip: int = Query(0, ge=0, description="Nombre de films à sauter (pagination)"),
    limit: int = Query(30, ge=1, le=100, description="Nombre max de films renvoyés"),
):
    """Liste les films du catalogue, avec filtres et pagination."""
    q = db.query(Film)

    if recherche:
        motif = f"%{recherche}%"
        q = q.filter(
            (Film.titre_francais.ilike(motif)) | (Film.titre_original.ilike(motif))
        )
    if annee is not None:
        q = q.filter(Film.annee == annee)
    if genre:
        q = q.join(Film.genres).filter(Genre.nom == genre)

    q = q.order_by(Film.note_public.desc().nullslast())
    return q.offset(skip).limit(limit).all()


@router.get("/{film_id}", response_model=FilmDetail)
def detail_film(film_id: int, db: Session = Depends(get_db)):
    """Fiche complète d'un film (genres, pays, thèmes, réalisateurs)."""
    film = db.query(Film).filter(Film.id == film_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Film introuvable.")
    return film
