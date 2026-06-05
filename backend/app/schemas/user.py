"""
schemas/user.py
---------------
Les « schémas » Pydantic décrivent la FORME des données qui entrent et sortent
de l'API. FastAPI s'en sert pour :
  - valider automatiquement ce que le client envoie (types, champs requis),
  - documenter l'API (Swagger),
  - filtrer ce qu'on renvoie (ne JAMAIS renvoyer le hash du mot de passe).

On sépare volontairement :
  - ce qu'on REÇOIT à l'inscription/connexion (avec mot de passe en clair),
  - ce qu'on RENVOIE (sans aucun mot de passe).
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Données reçues pour créer un compte."""
    email: EmailStr
    mot_de_passe: str = Field(min_length=8, description="Au moins 8 caractères")
    pseudo: str | None = None


class UserLogin(BaseModel):
    """Données reçues pour se connecter."""
    email: EmailStr
    mot_de_passe: str


class UserPublic(BaseModel):
    """Données renvoyées au client : jamais de mot de passe ni de hash."""
    id: int
    email: EmailStr
    pseudo: str | None
    cree_le: datetime

    # Permet à Pydantic de lire directement un objet SQLAlchemy (et pas qu'un dict).
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Réponse renvoyée après un login réussi."""
    access_token: str
    token_type: str = "bearer"
