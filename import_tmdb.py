"""
import_tmdb.py
--------------
Importe les films les mieux notés de TMDb, avec :
  - infos film (titres, année, durée, pays, genres),
  - réalisateurs + acteurs principaux,
  - thèmes (= keywords TMDb),
  - résumé Wikipédia (FR, repli EN),
  - notation interactive (vu ? note ?) film par film dans le terminal.

Prérequis : pip install requests ; cinema_db.py + notation.py dans le dossier.
Lance : export TMDB_API_KEY="ta_clé" puis python import_tmdb.py
"""

import os
import time
import requests

from cinema_db import Cinema
from notation import demander_vu_note, _demander_oui_non, _demander_note, _set_vu_note, Pause


CLE_API = os.environ.get("TMDB_API_KEY", "")
CHEMIN_BASE = "cinema.db"
LANGUE = "fr-FR"
NB_ACTEURS = 8

NB_FILMS = 250            # combien de films importer
VIDER_AVANT = False        # repartir d'une base propre

BASE_URL = "https://api.themoviedb.org/3"
HEADERS_WIKI = {"User-Agent": "cinemaprojet/1.0 (usage perso)"}


# ---------------------------------------------------------------------------
# Appels API TMDb
# ---------------------------------------------------------------------------

def _get(endpoint, **params):
    params["api_key"] = CLE_API
    params.setdefault("language", LANGUE)
    r = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def liste_top_rated(nb):
    """Renvoie une liste d'ids TMDb des films les mieux notés (pagine si besoin)."""
    ids = []
    page = 1
    while len(ids) < nb:
        data = _get("/movie/top_rated", page=page)
        resultats = data.get("results", [])
        if not resultats:
            break
        ids.extend(film["id"] for film in resultats)
        page += 1
        if page > data.get("total_pages", 1):
            break
    return ids[:nb]


def details_film(tmdb_id):
    # append_to_response : on récupère crédits + keywords en un seul appel
    return _get(f"/movie/{tmdb_id}", append_to_response="credits,keywords")


def details_personne(tmdb_id):
    return _get(f"/person/{tmdb_id}")


# ---------------------------------------------------------------------------
# Résumé Wikipédia (FR, repli EN) — robuste : ne casse jamais l'import
# ---------------------------------------------------------------------------

def resume_wikipedia(titre, annee=None, langues=("fr", "en")):
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
            # réseau, JSON invalide, etc. : on ignore et on tente la langue suivante
            continue
    return None


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def importer_personne(db, tmdb_id, type_):
    p = details_personne(tmdb_id)
    photo = p.get("profile_path")
    if photo:
        photo = f"https://image.tmdb.org/t/p/w500{photo}"
    return db.ajouter_personne(
        nom_complet=p.get("name"),
        type_=type_,
        naissance=p.get("birthday"),
        deces=p.get("deathday"),
        nationalite=p.get("place_of_birth"),
        photo=photo,
        tmdb_id=tmdb_id,
    )


def preparer_film(db, tmdb_id):
    """Récupère toutes les infos d'un film SANS rien écrire en base.
    Renvoie un dict prêt à insérer, ou None si déjà en base."""
    deja = db.conn.execute(
        "SELECT id FROM films WHERE tmdb_id = ?", (tmdb_id,)
    ).fetchone()
    if deja:
        return None

    d = details_film(tmdb_id)
    pays = [c["name"] for c in d.get("production_countries", [])]
    genres = [g["name"] for g in d.get("genres", [])]
    themes = [k["name"] for k in d.get("keywords", {}).get("keywords", [])]
    annee_sortie = (d.get("release_date") or "")[:4] or None
    annee = int(annee_sortie) if annee_sortie else None

    resume = resume_wikipedia(d.get("title") or d.get("original_title"), annee)

    affiche = d.get("poster_path")
    if affiche:
        affiche = f"https://image.tmdb.org/t/p/w500{affiche}"

    note_public = d.get("vote_average")

    return {
        "tmdb_id": tmdb_id,
        "titre_original": d.get("original_title"),
        "titre_francais": d.get("title"),
        "annee": annee,
        "annee_str": annee_sortie,
        "duree": d.get("runtime"),
        "pays": pays,
        "genres": genres,
        "themes": themes,
        "resume": resume,
        "affiche": affiche,
        "note_public": note_public,
        "credits": d.get("credits", {}),
        "titre": d.get("title") or d.get("original_title"),
        "nb_themes": len(themes),
        "resume_ok": resume is not None,
    }


def enregistrer_film(db, info):
    """Écrit en base un film préparé par preparer_film, + ses personnes/liens.
    Renvoie l'id du film créé."""
    film_id = db.ajouter_film(
        titre_original=info["titre_original"],
        titre_francais=info["titre_francais"],
        annee=info["annee"],
        duree=info["duree"],
        tmdb_id=info["tmdb_id"],
        pays=info["pays"],
        genres=info["genres"],
        themes=info["themes"],
        resume=info["resume"],
        affiche=info["affiche"],
        note_public=info["note_public"],
    )

    credits = info["credits"]
    for r in [m for m in credits.get("crew", []) if m.get("job") == "Director"]:
        db.lier_realisateur(film_id, importer_personne(db, r["id"], "réalisateur"))
    for a in credits.get("cast", [])[:NB_ACTEURS]:
        pid = importer_personne(db, a["id"], "acteur")
        db.lier_acteur(film_id, pid, role=a.get("character"), ordre=a.get("order"))

    return film_id

def main():
    if not CLE_API:
        print("⚠️  Aucune clé API. Fais : export TMDB_API_KEY=\"ta_clé\"")
        return

    db = Cinema(CHEMIN_BASE)
    if VIDER_AVANT:
        db.vider()
        print("Base vidée (repart propre).")

    print(f"Base : {db.chemin.resolve()}")
    print(f"Récupération des {NB_FILMS} films les mieux notés...\n")
    ids = liste_top_rated(NB_FILMS)
    print(f"{len(ids)} films à traiter.")
    print("(Tape 'stop' à la question vu/note pour mettre en pause.)\n")

    try:
        for i, tmdb_id in enumerate(ids, 1):
            try:
                info = preparer_film(db, tmdb_id)
            except requests.HTTPError as e:
                print(f"[{i}/{len(ids)}] ✗ erreur API : {e}")
                continue
            if info is None:
                continue  # déjà en base

            wiki = "résumé ✓" if info["resume_ok"] else "résumé ✗"
            print(f"[{i}/{len(ids)}] {info['titre']} ({info['annee_str']}) "
                  f"— {info['nb_themes']} thèmes, {wiki}")

            # On pose les questions AVANT d'écrire. Si 'stop' -> Pause, rien n'est inséré.
            vu = _demander_oui_non(f"As-tu vu « {info['titre']} » ?")
            note = _demander_note() if vu else None

            # Tout est répondu : on enregistre le film puis on pose vu/note.
            film_id = enregistrer_film(db, info)
            _set_vu_note(db, film_id, vu, note)
            if vu:
                txt = f"noté {note}/10" if note is not None else "sans note"
                print(f"  → enregistré et marqué vu ({txt}).")
            else:
                print("  → enregistré et marqué non vu.")
            time.sleep(0.2)
    except Pause:
        print("\n⏸  Session mise en pause. Aucun film laissé à moitié. Relance pour continuer.")


if __name__ == "__main__":
    main()