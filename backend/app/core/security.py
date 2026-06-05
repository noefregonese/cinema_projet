"""
core/security.py
----------------
Le cœur de la sécurité, deux responsabilités :

1. MOTS DE PASSE — On ne stocke jamais le mot de passe en clair. On en calcule
   une empreinte (hash) avec bcrypt. bcrypt est volontairement lent et « salé »
   (chaque hash est unique même pour deux mots de passe identiques), ce qui le
   rend résistant aux attaques. On ne peut pas inverser un hash ; on peut
   seulement VÉRIFIER qu'un mot de passe correspond à une empreinte.

2. JETONS JWT — Au login, on fabrique un petit jeton signé contenant l'id de
   l'utilisateur et une date d'expiration. Comme il est signé avec SECRET_KEY,
   personne ne peut le falsifier. Le frontend le renverra à chaque requête ;
   on le décodera pour savoir qui parle, sans avoir à stocker de session.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings


# ─── Mots de passe ───────────────────────────────────────────────────────────

def hacher_mot_de_passe(mot_de_passe: str) -> str:
    """Calcule l'empreinte bcrypt d'un mot de passe (à stocker en base)."""
    sel = bcrypt.gensalt()
    empreinte = bcrypt.hashpw(mot_de_passe.encode("utf-8"), sel)
    return empreinte.decode("utf-8")


def verifier_mot_de_passe(mot_de_passe: str, empreinte: str) -> bool:
    """Vérifie qu'un mot de passe correspond à une empreinte stockée."""
    return bcrypt.checkpw(
        mot_de_passe.encode("utf-8"), empreinte.encode("utf-8")
    )


# ─── Jetons JWT ──────────────────────────────────────────────────────────────

def creer_token(user_id: int) -> str:
    """Fabrique un JWT signé pour un utilisateur donné.

    Le champ standard 'sub' (subject) porte l'id de l'utilisateur ;
    'exp' (expiration) borne la durée de validité.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def lire_token(token: str) -> int | None:
    """Décode un JWT et renvoie l'id utilisateur, ou None si invalide/expiré."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        sub = payload.get("sub")
        return int(sub) if sub is not None else None
    except (JWTError, ValueError):
        return None
