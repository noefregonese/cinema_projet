"""
telecharger_donnees.py
----------------------
Télécharge l'export complet des données (tous les utilisateurs, leurs films
vus / pas vus / notes) depuis l'API EN LIGNE, et le sauvegarde dans un fichier
JSON local horodaté. Sert à alimenter le futur moteur de recommandations.

Configuration : renseigne tes deux valeurs ci-dessous (URL de l'API et tes
identifiants admin), ou passe-les en variables d'environnement.

Usage :
    python telecharger_donnees.py

Le fichier est écrit dans le dossier ./exports/ (créé au besoin).

Pour AUTOMATISER (ex. tous les jours à 9h), voir les instructions en bas.
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib import request, parse, error

# ─── Configuration ───────────────────────────────────────────────────────────
# URL de ton backend en ligne (Render), SANS slash final.
API_URL = os.environ.get("CINEMA_API_URL", "https://cinema-api-xxxx.onrender.com")
# Tes identifiants ADMIN (le compte que tu as promu via faire_admin.py).
EMAIL = os.environ.get("CINEMA_ADMIN_EMAIL", "ton.email@exemple.com")
MOT_DE_PASSE = os.environ.get("CINEMA_ADMIN_PASSWORD", "ton_mot_de_passe")

DOSSIER_SORTIE = Path(__file__).resolve().parent / "exports"


def _appel(chemin, methode="GET", form=None, token=None):
    url = f"{API_URL}{chemin}"
    data = parse.urlencode(form).encode() if form else None
    req = request.Request(url, data=data, method=methode)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if form:
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    print(f"Connexion à {API_URL} …")
    try:
        # 1. Login → token
        tok = _appel("/auth/login", "POST",
                     form={"username": EMAIL, "password": MOT_DE_PASSE})
        token = tok["access_token"]
        # 2. Export
        donnees = _appel("/admin/export", token=token)
    except error.HTTPError as e:
        if e.code == 403:
            print("✗ Ce compte n'est pas admin. Lance d'abord faire_admin.py.")
        elif e.code == 401:
            print("✗ Identifiants incorrects (EMAIL / MOT_DE_PASSE).")
        else:
            print(f"✗ Erreur HTTP {e.code} : {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Échec : {e}")
        print("  (Le backend met peut-être ~30s à se réveiller. Réessaie.)")
        sys.exit(1)

    # 3. Sauvegarde locale horodatée
    DOSSIER_SORTIE.mkdir(exist_ok=True)
    horodatage = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    fichier = DOSSIER_SORTIE / f"export_{horodatage}.json"
    fichier.write_text(json.dumps(donnees, ensure_ascii=False, indent=2), encoding="utf-8")

    nb_users = len(donnees.get("utilisateurs", []))
    nb_films = sum(u["nb_films"] for u in donnees.get("utilisateurs", []))
    print(f"✓ Export réussi : {nb_users} utilisateur(s), {nb_films} films au total.")
    print(f"  Fichier : {fichier}")


if __name__ == "__main__":
    main()
