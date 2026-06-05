"""
Regroupe tous les modèles pour que SQLAlchemy les enregistre tous sur Base
dès qu'on importe le package `app.models`. Indispensable : sans ça, les
relations qui pointent vers une table définie dans un autre fichier
(ex. "UserFilm" depuis film.py) ne se résolvent pas.
"""

from app.models.user import User
from app.models.film import Film
from app.models.user_film import UserFilm
from app.models.personne import Personne, FilmActeur, film_realisateurs
from app.models.vocab import (
    Pays, Genre, Theme,
    film_pays, film_genres, film_themes,
)

__all__ = [
    "User", "Film", "UserFilm",
    "Personne", "FilmActeur",
    "Pays", "Genre", "Theme",
]
