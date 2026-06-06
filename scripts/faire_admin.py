"""
faire_admin.py
--------------
Donne le statut admin à un compte (par son email). À lancer une seule fois
pour te désigner toi-même comme administrateur.

Usage (depuis le dossier backend/, avec le venv activé) :
    python ../scripts/faire_admin.py ton.email@exemple.com

Pour viser la base EN LIGNE (Neon) plutôt que la base locale, définis d'abord
DATABASE_URL dans ton terminal :
    export DATABASE_URL="postgresql://...ta connection string Neon..."
    python ../scripts/faire_admin.py ton.email@exemple.com
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.database import SessionLocal
import app.models  # noqa: F401  (enregistre les modèles)
from app.models.user import User


def main():
    if len(sys.argv) < 2:
        print("Usage : python faire_admin.py <email>")
        return
    email = sys.argv[1].strip()

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        print(f"Aucun compte avec l'email « {email} ».")
        print("Crée d'abord le compte sur le site, puis relance ce script.")
        db.close()
        return

    user.est_admin = True
    db.commit()
    print(f"✓ {email} est maintenant administrateur.")
    db.close()


if __name__ == "__main__":
    main()
