"""
routers/auth.py
---------------
Les endpoints d'authentification :

  POST /auth/register  → crée un compte
  POST /auth/login     → vérifie les identifiants, renvoie un token JWT
  GET  /auth/me        → renvoie l'utilisateur connecté (endpoint protégé)

C'est ici que se concrétise « se connecter au site ».
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserPublic, Token
from app.core.security import (
    hacher_mot_de_passe, verifier_mot_de_passe, creer_token,
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", response_model=UserPublic, status_code=201)
def register(donnees: UserCreate, db: Session = Depends(get_db)):
    """Crée un nouveau compte utilisateur."""
    # Email déjà pris ?
    existe = db.query(User).filter(User.email == donnees.email).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte existe déjà avec cet email.",
        )

    user = User(
        email=donnees.email,
        pseudo=donnees.pseudo,
        hash_mdp=hacher_mot_de_passe(donnees.mot_de_passe),
    )
    db.add(user)
    db.commit()
    db.refresh(user)        # recharge l'objet (récupère id, cree_le, etc.)
    return user


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Vérifie les identifiants et renvoie un token JWT.

    Format OAuth2 standard : le champ s'appelle `username` mais on y met
    l'email (ça fait marcher le bouton « Authorize » de Swagger).
    """
    user = db.query(User).filter(User.email == form.username).first()
    if user is None or not verifier_mot_de_passe(form.password, user.hash_mdp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
        )

    token = creer_token(user.id)
    return Token(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    """Renvoie l'utilisateur actuellement connecté (endpoint protégé)."""
    return user
