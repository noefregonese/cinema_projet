"""
vocab.py
--------
Vocabulaires partagés (pays, genres, thèmes) et leurs tables d'association
many-to-many avec les films.

Les associations ici ne portent AUCUNE donnée propre (juste « ce film a ce
genre »), donc on les déclare comme de simples objets Table, pas comme des
classes. SQLAlchemy s'en sert en coulisses via relationship(..., secondary=...).
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base


# ─── Tables d'association (film ↔ vocabulaire) ───────────────────────────────

film_pays = Table(
    "film_pays",
    Base.metadata,
    Column("film_id", ForeignKey("films.id", ondelete="CASCADE"), primary_key=True),
    Column("pays_id", ForeignKey("pays.id", ondelete="CASCADE"), primary_key=True),
)

film_genres = Table(
    "film_genres",
    Base.metadata,
    Column("film_id", ForeignKey("films.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

film_themes = Table(
    "film_themes",
    Base.metadata,
    Column("film_id", ForeignKey("films.id", ondelete="CASCADE"), primary_key=True),
    Column("theme_id", ForeignKey("themes.id", ondelete="CASCADE"), primary_key=True),
)


# ─── Tables de vocabulaire ───────────────────────────────────────────────────

class Pays(Base):
    __tablename__ = "pays"

    id = Column(Integer, primary_key=True)
    nom = Column(String, unique=True, nullable=False)

    films = relationship("Film", secondary=film_pays, back_populates="pays")


class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True)
    nom = Column(String, unique=True, nullable=False)

    films = relationship("Film", secondary=film_genres, back_populates="genres")


class Theme(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True)
    nom = Column(String, unique=True, nullable=False)

    films = relationship("Film", secondary=film_themes, back_populates="themes")
