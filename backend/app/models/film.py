"""
film.py
-------
Le film tel qu'il existe dans le CATALOGUE PARTAGÉ.

⚠️ Changement clé vs l'ancien schéma : les colonnes `vu`, `note`, `urgence`
ont DISPARU d'ici. Elles étaient propres à un utilisateur ; elles vivent
désormais dans la table user_films (un même film peut être vu par l'un,
pas par l'autre). Ce qui reste ici décrit le film objectivement.
"""

from sqlalchemy import Column, Integer, Float, String, Text, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.vocab import film_pays, film_genres, film_themes
from app.models.personne import film_realisateurs


class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True)
    titre_original = Column(String)
    titre_francais = Column(String)
    annee = Column(Integer, index=True)
    duree = Column(Integer)
    resume = Column(Text)
    affiche = Column(String)
    note_public = Column(Float)            # note TMDb (objective, partagée)
    tmdb_id = Column(Integer, unique=True)
    cree_le = Column(DateTime, server_default=func.now())

    # ─── Relations catalogue (partagées) ───
    pays = relationship("Pays", secondary=film_pays, back_populates="films")
    genres = relationship("Genre", secondary=film_genres, back_populates="films")
    themes = relationship("Theme", secondary=film_themes, back_populates="films")
    realisateurs = relationship(
        "Personne", secondary=film_realisateurs, back_populates="films_realises"
    )
    acteurs = relationship(
        "FilmActeur", back_populates="film", cascade="all, delete-orphan"
    )

    # ─── Relation données perso (par utilisateur) ───
    user_films = relationship(
        "UserFilm", back_populates="film", cascade="all, delete-orphan"
    )
