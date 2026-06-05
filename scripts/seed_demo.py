"""
seed_demo.py
------------
Injecte quelques films de démonstration dans la base, pour avoir de quoi
tester les endpoints /films et /me/films AVANT d'avoir branché l'import TMDb.

À lancer depuis le dossier backend/ (pour réutiliser la même base) :
    python ../scripts/seed_demo.py

Relançable sans créer de doublons (on saute les films déjà présents).
"""

import sys
from pathlib import Path

# Permet d'importer le package `app` depuis le dossier backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.database import SessionLocal, Base, engine
import app.models  # enregistre les modèles
from app.models.film import Film
from app.models.vocab import Genre

Base.metadata.create_all(bind=engine)

DEMO = [
    {"titre_francais": "Le Parrain", "titre_original": "The Godfather",
     "annee": 1972, "duree": 175, "note_public": 8.7, "tmdb_id": 238,
     "genres": ["Drame", "Crime"]},
    {"titre_francais": "Pulp Fiction", "titre_original": "Pulp Fiction",
     "annee": 1994, "duree": 154, "note_public": 8.5, "tmdb_id": 680,
     "genres": ["Thriller", "Crime"]},
    {"titre_francais": "Le Voyage de Chihiro", "titre_original": "千と千尋の神隠し",
     "annee": 2001, "duree": 125, "note_public": 8.5, "tmdb_id": 129,
     "genres": ["Animation", "Famille", "Fantastique"]},
    {"titre_francais": "Parasite", "titre_original": "기생충",
     "annee": 2019, "duree": 132, "note_public": 8.5, "tmdb_id": 496243,
     "genres": ["Thriller", "Drame", "Comédie"]},
    {"titre_francais": "Interstellar", "titre_original": "Interstellar",
     "annee": 2014, "duree": 169, "note_public": 8.4, "tmdb_id": 157336,
     "genres": ["Science-Fiction", "Drame", "Aventure"]},
]


def genre(db, nom):
    g = db.query(Genre).filter(Genre.nom == nom).first()
    if g is None:
        g = Genre(nom=nom)
        db.add(g)
        db.flush()
    return g


def main():
    db = SessionLocal()
    ajoutes = 0
    for d in DEMO:
        if db.query(Film).filter(Film.tmdb_id == d["tmdb_id"]).first():
            continue
        film = Film(
            titre_francais=d["titre_francais"],
            titre_original=d["titre_original"],
            annee=d["annee"],
            duree=d["duree"],
            note_public=d["note_public"],
            tmdb_id=d["tmdb_id"],
        )
        film.genres = [genre(db, n) for n in d["genres"]]
        db.add(film)
        ajoutes += 1
    db.commit()
    total = db.query(Film).count()
    print(f"{ajoutes} film(s) ajouté(s). Total en base : {total}.")
    db.close()


if __name__ == "__main__":
    main()
