"""
personne.py
-----------
Personnes (réalisateurs, acteurs) et leurs liens avec les films.

- film ↔ réalisateur : lien simple, pas de donnée propre → Table d'association.
- film ↔ acteur      : porte `role` et `ordre` → classe complète (FilmActeur).
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base


# film ↔ réalisateur : association simple
film_realisateurs = Table(
    "film_realisateurs",
    Base.metadata,
    Column("film_id", ForeignKey("films.id", ondelete="CASCADE"), primary_key=True),
    Column("personne_id", ForeignKey("personnes.id", ondelete="CASCADE"), primary_key=True),
)


class Personne(Base):
    __tablename__ = "personnes"

    id = Column(Integer, primary_key=True)
    nom_complet = Column(String, nullable=False, index=True)
    type = Column(String)                 # "réalisateur" / "acteur"
    naissance = Column(String)
    deces = Column(String)
    nationalite = Column(String)
    genres_principaux = Column(String)
    photo = Column(String)
    tmdb_id = Column(Integer, unique=True)

    # Films réalisés (via l'association simple)
    films_realises = relationship(
        "Film", secondary=film_realisateurs, back_populates="realisateurs"
    )
    # Rôles d'acteur (via la classe FilmActeur)
    roles = relationship("FilmActeur", back_populates="personne")


class FilmActeur(Base):
    """Lien film ↔ acteur qui porte des données propres (rôle, ordre au générique)."""

    __tablename__ = "film_acteurs"

    film_id = Column(ForeignKey("films.id", ondelete="CASCADE"), primary_key=True)
    personne_id = Column(ForeignKey("personnes.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String)
    ordre = Column(Integer)

    film = relationship("Film", back_populates="acteurs")
    personne = relationship("Personne", back_populates="roles")
