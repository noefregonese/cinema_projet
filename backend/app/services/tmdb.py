"""
services/tmdb.py
----------------
Toute la logique d'import TMDb, isolée du web (pas de FastAPI ici, pas d'input()).

Reprend le cœur de l'ancien import_tmdb.py, mais :
  - écrit en base via SQLAlchemy (et non l'ancienne classe Cinema),
  - ne pose aucune question : le « vu / note » sera géré côté utilisateur
    via les endpoints /me/films qu'on a déjà construits,
  - renvoie des objets Python, les endpoints s'occupent du HTTP.

Fonctions principales :
  - rechercher(q)              : cherche des films sur TMDb (pour l'autocomplétion)
  - importer_film(db, tmdb_id) : importe un film complet dans le catalogue
"""

import requests

from sqlalchemy.orm import Session

from app.config import settings
from app.models.film import Film
from app.models.personne import Personne, FilmActeur
from app.models.vocab import Pays, Genre, Theme

BASE_URL = "https://api.themoviedb.org/3"
LANGUE = "fr-FR"
NB_ACTEURS = 8
HEADERS_WIKI = {"User-Agent": "cinemaprojet/1.0 (usage perso)"}
IMG = "https://image.tmdb.org/t/p/w500"


# ─── Appels TMDb ─────────────────────────────────────────────────────────────

def _get(endpoint: str, **params):
    if not settings.TMDB_API_KEY:
        raise RuntimeError("Clé TMDB_API_KEY absente : renseigne-la dans le .env")
    params["api_key"] = settings.TMDB_API_KEY
    params.setdefault("language", LANGUE)
    r = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def rechercher(query: str, limite: int = 8) -> list[dict]:
    """Cherche des films sur TMDb. Renvoie une liste allégée pour l'UI."""
    data = _get("/search/movie", query=query)
    out = []
    for r in data.get("results", [])[:limite]:
        out.append({
            "tmdb_id": r["id"],
            "titre": r.get("title") or r.get("original_title"),
            "annee": (r.get("release_date") or "")[:4] or None,
            "affiche": f"{IMG}{r['poster_path']}" if r.get("poster_path") else None,
            "note_public": r.get("vote_average"),
        })
    return out


def _details_film(tmdb_id: int):
    return _get(f"/movie/{tmdb_id}", append_to_response="credits,keywords")


def _details_personne(tmdb_id: int):
    return _get(f"/person/{tmdb_id}")


# ─── Résumé Wikipédia (robuste : ne casse jamais l'import) ────────────────────

def _resume_wikipedia(titre, annee=None, langues=("fr", "en")):
    for lang in langues:
        try:
            recherche = requests.get(
                f"https://{lang}.wikipedia.org/w/api.php",
                params={
                    "action": "query", "list": "search",
                    "srsearch": f"{titre} film {annee}" if annee else f"{titre} film",
                    "format": "json", "srlimit": 1,
                },
                timeout=10, headers=HEADERS_WIKI,
            )
            hits = recherche.json().get("query", {}).get("search", [])
            if not hits:
                continue
            page = hits[0]["title"]
            extrait_req = requests.get(
                f"https://{lang}.wikipedia.org/w/api.php",
                params={
                    "action": "query", "prop": "extracts",
                    "exintro": 1, "explaintext": 1,
                    "titles": page, "format": "json",
                },
                timeout=10, headers=HEADERS_WIKI,
            )
            pages = extrait_req.json().get("query", {}).get("pages", {})
            for _, v in pages.items():
                extrait = (v.get("extract") or "").strip()
                if extrait:
                    return extrait
        except Exception:
            continue
    return None


# ─── Helpers vocabulaire / personnes (dédoublonnage) ─────────────────────────

def _vocab(db: Session, modele, nom: str):
    """Récupère ou crée une entrée de vocabulaire (genre, pays, thème)."""
    nom = nom.strip()
    obj = db.query(modele).filter(modele.nom == nom).first()
    if obj is None:
        obj = modele(nom=nom)
        db.add(obj)
        db.flush()
    return obj


def _personne(db: Session, tmdb_id: int, type_: str) -> Personne:
    """Récupère ou crée une personne (par son tmdb_id)."""
    p = db.query(Personne).filter(Personne.tmdb_id == tmdb_id).first()
    if p is not None:
        return p
    info = _details_personne(tmdb_id)
    photo = info.get("profile_path")
    p = Personne(
        nom_complet=info.get("name"),
        type=type_,
        naissance=info.get("birthday"),
        deces=info.get("deathday"),
        nationalite=info.get("place_of_birth"),
        photo=f"{IMG}{photo}" if photo else None,
        tmdb_id=tmdb_id,
    )
    db.add(p)
    db.flush()
    return p


# ─── Import principal ────────────────────────────────────────────────────────

def importer_film(db: Session, tmdb_id: int) -> Film:
    """Importe un film TMDb dans le catalogue (ou le renvoie s'il existe déjà).

    Crée le film, ses genres/pays/thèmes, ses réalisateurs et acteurs,
    et tente de récupérer un résumé Wikipédia.
    """
    existant = db.query(Film).filter(Film.tmdb_id == tmdb_id).first()
    if existant is not None:
        return existant

    d = _details_film(tmdb_id)
    annee_str = (d.get("release_date") or "")[:4] or None
    annee = int(annee_str) if annee_str else None
    affiche = d.get("poster_path")

    film = Film(
        tmdb_id=tmdb_id,
        titre_original=d.get("original_title"),
        titre_francais=d.get("title"),
        annee=annee,
        duree=d.get("runtime"),
        note_public=d.get("vote_average"),
        affiche=f"{IMG}{affiche}" if affiche else None,
        resume=_resume_wikipedia(d.get("title") or d.get("original_title"), annee),
    )

    film.pays = [_vocab(db, Pays, c["name"]) for c in d.get("production_countries", [])]
    film.genres = [_vocab(db, Genre, g["name"]) for g in d.get("genres", [])]
    film.themes = [
        _vocab(db, Theme, k["name"])
        for k in d.get("keywords", {}).get("keywords", [])
    ]

    credits = d.get("credits", {})
    # Réalisateurs
    for membre in [m for m in credits.get("crew", []) if m.get("job") == "Director"]:
        film.realisateurs.append(_personne(db, membre["id"], "réalisateur"))
    # Acteurs principaux (avec rôle et ordre)
    db.add(film)
    db.flush()
    for a in credits.get("cast", [])[:NB_ACTEURS]:
        pers = _personne(db, a["id"], "acteur")
        db.add(FilmActeur(
            film_id=film.id, personne_id=pers.id,
            role=a.get("character"), ordre=a.get("order"),
        ))

    db.commit()
    db.refresh(film)
    return film
