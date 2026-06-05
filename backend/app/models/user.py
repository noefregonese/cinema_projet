"""
user.py
-------
Les comptes utilisateurs.

⚠️ On ne stocke JAMAIS le mot de passe en clair : seulement son empreinte
(hash bcrypt), calculée dans core/security.py. Même nous, en lisant la base,
ne pouvons pas retrouver le mot de passe d'origine.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    pseudo = Column(String)
    hash_mdp = Column(String, nullable=False)     # empreinte bcrypt, jamais le mdp
    actif = Column(Boolean, default=True)
    cree_le = Column(DateTime, server_default=func.now())

    # Tous les liens de cet utilisateur vers des films (vu/note/urgence)
    films = relationship(
        "UserFilm", back_populates="user", cascade="all, delete-orphan"
    )
