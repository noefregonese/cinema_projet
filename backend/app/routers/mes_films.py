"""
routers/mes_films.py
--------------------
Les données PERSONNELLES de l'utilisateur connecté. Tout est protégé :
chaque endpoint passe par get_current_user, donc on ne lit/écrit QUE les
lignes user_films appartenant à cet utilisateur.

  GET    /me/films            → mes films (vu/note/urgence), filtrable
  PUT    /me/films/{film_id}  → marquer vu / noter / mettre une urgence
  DELETE /me/films/{film_id}  → retirer un film de ma liste

C'est ici que « être connecté à sa base » se concrétise : le même film a un
statut différent selon l'utilisateur, et personne ne voit le statut des autres.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.film import Film
from app.models.user_film import UserFilm
from app.schemas.film import FilmAvecStatut, StatutPerso, StatutUpdate

router = APIRouter(prefix="/me/films", tags=["Mes films"])


@router.get("", response_model=list[FilmAvecStatut])
def mes_films(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    vu: bool | None = Query(None, description="Filtre : vus (true) ou à voir (false)"),
):
    """Liste les films que l'utilisateur a dans sa liste, avec son statut."""
    q = (
        db.query(UserFilm)
        .filter(UserFilm.user_id == user.id)
        .join(Film, UserFilm.film_id == Film.id)
    )
    if vu is not None:
        q = q.filter(UserFilm.vu == vu)

    q = q.order_by(UserFilm.urgence.desc(), Film.annee.desc())

    return [
        FilmAvecStatut(film=uf.film, statut=StatutPerso.model_validate(uf))
        for uf in q.all()
    ]


@router.put("/{film_id}", response_model=StatutPerso)
def maj_statut(
    film_id: int,
    maj: StatutUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Crée ou met à jour le statut de l'utilisateur sur un film.

    Si l'utilisateur n'avait pas encore ce film dans sa liste, on crée la ligne.
    On ne modifie que les champs fournis (les autres restent inchangés).
    """
    # Le film doit exister dans le catalogue.
    film = db.query(Film).filter(Film.id == film_id).first()
    if film is None:
        raise HTTPException(status_code=404, detail="Film introuvable.")

    # Ligne user_films existante ?
    uf = (
        db.query(UserFilm)
        .filter(UserFilm.user_id == user.id, UserFilm.film_id == film_id)
        .first()
    )
    if uf is None:
        uf = UserFilm(user_id=user.id, film_id=film_id)
        db.add(uf)

    # On applique seulement ce qui est fourni (exclude_unset).
    donnees = maj.model_dump(exclude_unset=True)
    if "vu" in donnees:
        uf.vu = donnees["vu"]
        # Note la date de visionnage la première fois qu'on marque vu.
        if donnees["vu"] and uf.vu_le is None:
            uf.vu_le = datetime.now(timezone.utc)
    if "note" in donnees:
        uf.note = donnees["note"]
    if "urgence" in donnees:
        uf.urgence = donnees["urgence"]

    db.commit()
    db.refresh(uf)
    return uf


@router.delete("/{film_id}", status_code=204)
def retirer_film(
    film_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Retire un film de la liste personnelle de l'utilisateur."""
    uf = (
        db.query(UserFilm)
        .filter(UserFilm.user_id == user.id, UserFilm.film_id == film_id)
        .first()
    )
    if uf is None:
        raise HTTPException(status_code=404, detail="Ce film n'est pas dans ta liste.")
    db.delete(uf)
    db.commit()
