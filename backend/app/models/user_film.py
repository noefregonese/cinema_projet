"""
user_film.py
------------
LE cœur du multi-utilisateur.

Cette table relie un utilisateur à un film et porte tout ce qui est PERSONNEL :
vu / pas vu, note, urgence, date de visionnage. C'est l'équivalent des anciennes
colonnes de `films`, mais désormais une ligne PAR (utilisateur, film).

Exemple : le film 42 peut avoir
  - (user 1, film 42, vu=1, note=9)
  - (user 2, film 42, vu=0, note=NULL, urgence=1)
sans aucun conflit.

La clé primaire composite (user_id, film_id) garantit qu'un utilisateur n'a
qu'une seule ligne par film.
"""

from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class UserFilm(Base):
    __tablename__ = "user_films"

    user_id = Column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    film_id = Column(
        ForeignKey("films.id", ondelete="CASCADE"), primary_key=True
    )

    vu = Column(Boolean, default=False)
    note = Column(Float)                       # 0–10, ou NULL si pas noté
    urgence = Column(Integer, default=0)       # priorité dans la liste à voir
    vu_le = Column(DateTime)                   # quand l'utilisateur l'a vu
    ajoute_le = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="films")
    film = relationship("Film", back_populates="user_films")
