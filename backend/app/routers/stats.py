"""
routers/stats.py
----------------
Statistiques de la filmothèque personnelle (films VUS de l'utilisateur).

  GET /me/stats  → chiffres + agrégats pour la page « Ma filmothèque »

Tout est calculé côté serveur à partir des films vus : nombre, note moyenne,
répartition par genre / pays / décennie, distribution des notes, coups de cœur.
"""

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.film import Film
from app.models.user_film import UserFilm

router = APIRouter(prefix="/me/stats", tags=["Statistiques"])


@router.get("")
def mes_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Agrège les statistiques des films VUS par l'utilisateur."""
    # On récupère les films vus avec leur statut, en une fois.
    lignes = (
        db.query(UserFilm, Film)
        .join(Film, UserFilm.film_id == Film.id)
        .filter(UserFilm.user_id == user.id, UserFilm.vu == True)  # noqa: E712
        .all()
    )

    total = len(lignes)
    if total == 0:
        return {
            "total_vus": 0, "note_moyenne": None, "nb_notes": 0,
            "genres": [], "pays": [], "decennies": [],
            "distribution_notes": [], "coups_de_coeur": [],
        }

    notes = [uf.note for uf, _ in lignes if uf.note is not None]
    note_moyenne = round(sum(notes) / len(notes), 2) if notes else None

    # Compteurs
    genres = Counter()
    pays = Counter()
    decennies = Counter()
    for _, film in lignes:
        for g in film.genres:
            genres[g.nom] += 1
        for p in film.pays:
            pays[p.nom] += 1
        if film.annee:
            decennies[(film.annee // 10) * 10] += 1

    # Distribution des notes (par entier de 1 à 10)
    dist = Counter(round(n) for n in notes)
    distribution = [{"note": i, "nb": dist.get(i, 0)} for i in range(1, 11)]

    # Coups de cœur : les 6 mieux notés
    notes_films = sorted(
        [(uf.note, film) for uf, film in lignes if uf.note is not None],
        key=lambda x: x[0], reverse=True,
    )[:6]
    coups_de_coeur = [
        {
            "id": film.id,
            "titre": film.titre_francais or film.titre_original,
            "annee": film.annee,
            "affiche": film.affiche,
            "note": note,
        }
        for note, film in notes_films
    ]

    def top(compteur, n=6):
        return [{"nom": nom, "nb": nb} for nom, nb in compteur.most_common(n)]

    return {
        "total_vus": total,
        "note_moyenne": note_moyenne,
        "nb_notes": len(notes),
        "genres": top(genres),
        "pays": top(pays),
        "decennies": [
            {"decennie": d, "nb": n} for d, n in sorted(decennies.items())
        ],
        "distribution_notes": distribution,
        "coups_de_coeur": coups_de_coeur,
    }
