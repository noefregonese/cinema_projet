"""
core/deps.py
------------
Les « dépendances » FastAPI : des fonctions qu'on branche sur un endpoint pour
qu'elles s'exécutent avant lui.

get_current_user est la pièce qui PROTÈGE un endpoint :
  1. FastAPI extrait le token du header « Authorization: Bearer <token> ».
  2. On décode le token → on obtient l'id utilisateur.
  3. On va chercher l'utilisateur en base.
  4. Si quoi que ce soit échoue → erreur 401 (non authentifié).
  5. Sinon, l'endpoint reçoit directement l'objet User connecté.

Pour protéger un endpoint, il suffira d'écrire :
    def mon_endpoint(user: User = Depends(get_current_user)):
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import lire_token
from app.models.user import User

# Indique à FastAPI où se trouve l'endpoint de login (pour la doc Swagger,
# le bouton « Authorize »). tokenUrl est relatif à la racine de l'API.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    erreur_401 = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou session expirée.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = lire_token(token)
    if user_id is None:
        raise erreur_401

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.actif:
        raise erreur_401

    return user


def get_admin(user: User = Depends(get_current_user)) -> User:
    """Comme get_current_user, mais exige en plus que l'utilisateur soit admin.
    Sert à protéger les endpoints d'export/administration."""
    if not user.est_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé à l'administrateur.",
        )
    return user
