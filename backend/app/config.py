"""
config.py
---------
Centralise la configuration lue depuis l'environnement (.env).

On lit les variables une seule fois ici, et le reste du code importe `settings`.
Ça évite d'éparpiller des os.environ.get(...) partout et de se tromper de nom.
"""

import os
from pathlib import Path

# Charge le fichier .env s'il existe (cherché à la racine du projet).
# python-dotenv est optionnel : si absent, on lit juste l'environnement système.
try:
    from dotenv import load_dotenv
    # .env est à la racine cinema/, soit deux niveaux au-dessus de ce fichier
    racine = Path(__file__).resolve().parents[2]
    load_dotenv(racine / ".env")
except ImportError:
    pass


class Settings:
    # Clé secrète qui signe les tokens JWT. SANS valeur par défaut sûre :
    # on met une valeur de dev, mais en prod elle DOIT venir du .env.
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-a-changer")

    # Algorithme de signature des JWT.
    ALGORITHM: str = "HS256"

    # Durée de validité d'un token, en minutes (défaut : 7 jours).
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")
    )

    # Clé API TMDb (pour l'import, étape ultérieure).
    TMDB_API_KEY: str = os.environ.get("TMDB_API_KEY", "")

    # URL de la base.
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./cinema.db")


settings = Settings()
