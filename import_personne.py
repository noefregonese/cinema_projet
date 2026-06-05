"""
import_personne.py
------------------
Alimente la base à partir d'une PERSONNE (réalisateur ou acteur).
Tu tapes un nom, le script gère les homonymes, te demande réalisateur
ou acteur, puis te fait défiler ses films un par un (vu ? note ?),
en sautant ceux déjà en base (relançable sans doublon).

Lance : export TMDB_API_KEY="ta_clé" puis python import_personne.py
"""

import os
import requests

from cinema_db import Cinema
from notation import demander_vu_note
import import_tmdb as imp   # on réutilise importer_film, _get, etc.


def chercher_personnes(nom):
    """Renvoie une liste de candidats {id, name, dept, connus}."""
    data = imp._get("/search/person", query=nom)
    out = []
    for r in data.get("results", [])[:8]:
        connus = [k.get("title") or k.get("name") for k in r.get("known_for", [])]
        connus = [c for c in connus if c][:3]
        out.append({
            "id": r["id"],
            "name": r["name"],
            "dept": r.get("known_for_department", "?"),
            "connus": connus,
        })
    return out


def choisir_personne(nom):
    candidats = chercher_personnes(nom)
    if not candidats:
        print(f"Aucune personne trouvée pour « {nom} ».")
        return None
    if len(candidats) == 1:
        c = candidats[0]
        print(f"Trouvé : {c['name']} ({c['dept']})")
        return c
    print("Plusieurs personnes correspondent :")
    for i, c in enumerate(candidats, 1):
        connus = ", ".join(c["connus"]) if c["connus"] else "—"
        print(f"  [{i}] {c['name']} ({c['dept']}) — connu pour : {connus}")
    choix = input("Numéro de la bonne personne (Entrée pour annuler) : ").strip()
    if not choix.isdigit() or not (1 <= int(choix) <= len(candidats)):
        print("Annulé.")
        return None
    return candidats[int(choix) - 1]


def filmographie(personne_id, role):
    """role = 'realisateur' ou 'acteur'. Renvoie une liste d'ids TMDb de films."""
    data = imp._get(f"/person/{personne_id}/movie_credits")
    if role == "acteur":
        films = data.get("cast", [])
    else:  # réalisateur
        films = [m for m in data.get("crew", []) if m.get("job") == "Director"]
    # dédoublonne et trie par date
    vus = {}
    for f in films:
        vus[f["id"]] = f.get("release_date", "")
    return [fid for fid, _ in sorted(vus.items(), key=lambda x: x[1] or "9999")]


def main():
    if not imp.CLE_API:
        print("⚠️  Aucune clé API. Fais : export TMDB_API_KEY=\"ta_clé\"")
        return

    from notation import Pause

    nom = input("Nom du réalisateur ou de l'acteur/actrice : ").strip()
    if not nom:
        print("Aucun nom saisi.")
        return

    personne = choisir_personne(nom)
    if personne is None:
        return

    role_in = input("Ses films comme (r)éalisateur ou (a)cteur ? ").strip().lower()
    role = "realisateur" if role_in.startswith("r") else "acteur"

    ids = filmographie(personne["id"], role)
    if not ids:
        print(f"Aucun film trouvé pour {personne['name']} en tant que {role}.")
        return

    db = Cinema(imp.CHEMIN_BASE)

    deja = 0
    a_traiter = []
    for fid in ids:
        existe = db.conn.execute(
            "SELECT id FROM films WHERE tmdb_id = ?", (fid,)
        ).fetchone()
        if existe:
            deja += 1
        else:
            a_traiter.append(fid)

    print(f"\n{personne['name']} ({role}) : {len(ids)} films "
          f"— {deja} déjà en base, {len(a_traiter)} à traiter.")
    print("(Tape 'stop' à la question vu/note pour mettre en pause.)\n")

    try:
        for i, fid in enumerate(a_traiter, 1):
            try:
                info = imp.preparer_film(db, fid)
            except requests.HTTPError as e:
                print(f"[{i}/{len(a_traiter)}] ✗ erreur API : {e}")
                continue
            if info is None:
                continue

            wiki = "résumé ✓" if info["resume_ok"] else "résumé ✗"
            print(f"[{i}/{len(a_traiter)}] {info['titre']} ({info['annee_str']}) "
                  f"— {info['nb_themes']} thèmes, {wiki}")

            vu = imp._demander_oui_non(f"As-tu vu « {info['titre']} » ?")
            note = imp._demander_note() if vu else None

            film_id = imp.enregistrer_film(db, info)
            imp._set_vu_note(db, film_id, vu, note)
            if vu:
                txt = f"noté {note}/10" if note is not None else "sans note"
                print(f"  → enregistré et marqué vu ({txt}).")
            else:
                print("  → enregistré et marqué non vu.")
    except imp.Pause:
        print("\n⏸  Session mise en pause. Aucun film laissé à moitié. Relance pour continuer.")