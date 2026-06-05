"""
notation.py
-----------
Gestion vu / note, avec pause propre ('stop').
"""

from cinema_db import Cinema


class Pause(Exception):
    """Levée quand l'utilisateur tape 'stop' pour interrompre proprement."""
    pass


def _demander_oui_non(question):
    while True:
        rep = input(f"{question} (o/n, ou 'stop' pour quitter) : ").strip().lower()
        if rep == "stop":
            raise Pause()
        if rep in ("o", "oui", "y", "yes"):
            return True
        if rep in ("n", "non", "no"):
            return False
        print("  Réponds par 'o' (oui), 'n' (non), ou 'stop'.")


def _demander_note():
    while True:
        rep = input("Quelle note de 0 à 10 ? (Entrée pour passer, 'stop' pour quitter) : ").strip().replace(",", ".")
        if rep == "stop":
            raise Pause()
        if rep == "":
            return None
        try:
            note = float(rep)
        except ValueError:
            print("  Entre un nombre, par ex. 8 ou 7.5.")
            continue
        if 0 <= note <= 10:
            return note
        print("  La note doit être entre 0 et 10.")


def _set_vu_note(db, film_id, vu, note):
    db.conn.execute(
        "UPDATE films SET vu = ?, note = ? WHERE id = ?",
        (int(vu), note, film_id),
    )
    db.conn.commit()


def _trouver_film(db, titre):
    rows = db.conn.execute(
        """SELECT id, titre_francais, titre_original, annee FROM films
           WHERE titre_francais LIKE ? OR titre_original LIKE ?
           ORDER BY annee""",
        (f"%{titre}%", f"%{titre}%"),
    ).fetchall()

    if not rows:
        print(f"Aucun film trouvé pour « {titre} ».")
        return None
    if len(rows) == 1:
        return rows[0]

    print(f"Plusieurs films correspondent à « {titre} » :")
    for r in rows:
        print(f"  [{r['id']}] {r['titre_francais']} ({r['annee']})")
    choix = input("Indique l'id du bon film : ").strip()
    for r in rows:
        if str(r["id"]) == choix:
            return r
    print("Id non reconnu.")
    return None


def demander_vu_note(db, film_id, titre_affiche=""):
    """Pose vu ? puis note ?. Lève Pause si l'utilisateur tape 'stop'."""
    vu = _demander_oui_non(f"As-tu vu « {titre_affiche} » ?")
    note = _demander_note() if vu else None
    _set_vu_note(db, film_id, vu, note)
    if vu:
        txt = f"noté {note}/10" if note is not None else "sans note"
        print(f"  → marqué comme vu ({txt}).")
    else:
        print("  → marqué comme non vu.")


def marquer_vu(titre, note=None, chemin_base="cinema.db"):
    """Dit après coup que tu as vu un film (par titre), avec note optionnelle."""
    db = Cinema(chemin_base)
    film = _trouver_film(db, titre)
    if film is None:
        db.fermer()
        return
    if note is None:
        note = _demander_note()
    elif not (0 <= note <= 10):
        print("La note doit être entre 0 et 10. Annulé.")
        db.fermer()
        return
    _set_vu_note(db, film["id"], True, note)
    txt = f"noté {note}/10" if note is not None else "sans note"
    print(f"« {film['titre_francais']} » ({film['annee']}) marqué vu, {txt}.")
    db.fermer()


def noter(titre, note=None, chemin_base="cinema.db"):
    """(Re)met une note à un film. Le marque aussi comme vu."""
    marquer_vu(titre, note=note, chemin_base=chemin_base)


if __name__ == "__main__":
    db = Cinema("cinema.db")
    films = db.conn.execute(
        "SELECT id, titre_francais, annee, vu, note FROM films ORDER BY annee"
    ).fetchall()
    print("Films en base :")
    for f in films:
        statut = "vu" if f["vu"] else "non vu"
        note = f" — {f['note']}/10" if f["note"] is not None else ""
        print(f"  [{f['id']}] {f['titre_francais']} ({f['annee']}) — {statut}{note}")
    db.fermer()