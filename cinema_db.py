"""
cinema_db.py
------------
Base de données relationnelle SQLite pour un projet de culture cinématographique.
"""

import sqlite3
from pathlib import Path
from typing import Iterable, Optional


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS films (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    titre_original  TEXT,
    titre_francais  TEXT,
    annee           INTEGER,
    duree           INTEGER,
    note            REAL,
    vu              INTEGER DEFAULT 0,
    urgence         INTEGER DEFAULT 0,
    resume          TEXT,
    affiche         TEXT,
    note_public     REAL,
    tmdb_id         INTEGER UNIQUE,
    cree_le         TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS personnes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_complet       TEXT NOT NULL,
    type              TEXT,
    naissance         TEXT,
    deces             TEXT,
    nationalite       TEXT,
    genres_principaux TEXT,
    photo             TEXT,
    tmdb_id           INTEGER UNIQUE,
    cree_le           TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pays (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nom  TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS themes (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nom  TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS genres (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nom  TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS film_realisateurs (
    film_id     INTEGER NOT NULL REFERENCES films(id)     ON DELETE CASCADE,
    personne_id INTEGER NOT NULL REFERENCES personnes(id) ON DELETE CASCADE,
    PRIMARY KEY (film_id, personne_id)
);

CREATE TABLE IF NOT EXISTS film_acteurs (
    film_id     INTEGER NOT NULL REFERENCES films(id)     ON DELETE CASCADE,
    personne_id INTEGER NOT NULL REFERENCES personnes(id) ON DELETE CASCADE,
    role        TEXT,
    ordre       INTEGER,
    PRIMARY KEY (film_id, personne_id)
);

CREATE TABLE IF NOT EXISTS film_pays (
    film_id INTEGER NOT NULL REFERENCES films(id) ON DELETE CASCADE,
    pays_id INTEGER NOT NULL REFERENCES pays(id)  ON DELETE CASCADE,
    PRIMARY KEY (film_id, pays_id)
);

CREATE TABLE IF NOT EXISTS film_themes (
    film_id  INTEGER NOT NULL REFERENCES films(id)  ON DELETE CASCADE,
    theme_id INTEGER NOT NULL REFERENCES themes(id) ON DELETE CASCADE,
    PRIMARY KEY (film_id, theme_id)
);

CREATE TABLE IF NOT EXISTS film_genres (
    film_id  INTEGER NOT NULL REFERENCES films(id)  ON DELETE CASCADE,
    genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (film_id, genre_id)
);

CREATE INDEX IF NOT EXISTS idx_films_annee   ON films(annee);
CREATE INDEX IF NOT EXISTS idx_personnes_nom ON personnes(nom_complet);
"""


class Cinema:
    """Façade simple autour de la base SQLite."""

    def __init__(self, chemin: str = "cinema.db"):
        self.chemin = Path(chemin)
        self.chemin.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.chemin)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def _id_vocab(self, table: str, nom: str) -> int:
        nom = nom.strip()
        cur = self.conn.execute(f"SELECT id FROM {table} WHERE nom = ?", (nom,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur = self.conn.execute(f"INSERT INTO {table} (nom) VALUES (?)", (nom,))
        return cur.lastrowid

    def ajouter_film(
        self,
        titre_original=None,
        titre_francais=None,
        annee=None,
        duree=None,
        note=None,
        vu=False,
        urgence=False,
        resume=None,
        affiche=None,
        note_public=None,
        tmdb_id=None,
        pays=None,
        themes=None,
        genres=None,
    ):
        cur = self.conn.execute(
            """INSERT INTO films
               (titre_original, titre_francais, annee, duree, note, vu, urgence, resume, affiche, note_public, tmdb_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (titre_original, titre_francais, annee, duree, note,
             int(vu), int(urgence), resume, affiche, note_public, tmdb_id),
        )
        film_id = cur.lastrowid

        for nom in pays or []:
            self.conn.execute(
                "INSERT OR IGNORE INTO film_pays (film_id, pays_id) VALUES (?, ?)",
                (film_id, self._id_vocab("pays", nom)),
            )
        for nom in themes or []:
            self.conn.execute(
                "INSERT OR IGNORE INTO film_themes (film_id, theme_id) VALUES (?, ?)",
                (film_id, self._id_vocab("themes", nom)),
            )
        for nom in genres or []:
            self.conn.execute(
                "INSERT OR IGNORE INTO film_genres (film_id, genre_id) VALUES (?, ?)",
                (film_id, self._id_vocab("genres", nom)),
            )

        self.conn.commit()
        return film_id

    def ajouter_personne(
        self,
        nom_complet: str,
        type_: Optional[str] = None,
        naissance: Optional[str] = None,
        deces: Optional[str] = None,
        nationalite: Optional[str] = None,
        genres_principaux: Optional[str] = None,
        photo: Optional[str] = None,
        tmdb_id: Optional[int] = None,
    ) -> int:
        if tmdb_id is not None:
            row = self.conn.execute(
                "SELECT id FROM personnes WHERE tmdb_id = ?", (tmdb_id,)
            ).fetchone()
            if row:
                return row["id"]

        cur = self.conn.execute(
            """INSERT INTO personnes
               (nom_complet, type, naissance, deces, nationalite,
                genres_principaux, photo, tmdb_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (nom_complet, type_, naissance, deces, nationalite,
             genres_principaux, photo, tmdb_id),
        )
        self.conn.commit()
        return cur.lastrowid

    def lier_realisateur(self, film_id: int, personne_id: int) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO film_realisateurs (film_id, personne_id) VALUES (?, ?)",
            (film_id, personne_id),
        )
        self.conn.commit()

    def lier_acteur(
        self, film_id: int, personne_id: int,
        role: Optional[str] = None, ordre: Optional[int] = None,
    ) -> None:
        self.conn.execute(
            """INSERT OR IGNORE INTO film_acteurs (film_id, personne_id, role, ordre)
               VALUES (?, ?, ?, ?)""",
            (film_id, personne_id, role, ordre),
        )
        self.conn.commit()

    def vider(self) -> None:
        """Efface toutes les données (repart d'une base propre)."""
        for t in ["film_realisateurs", "film_acteurs", "film_pays",
                  "film_themes", "film_genres", "films", "personnes",
                  "pays", "themes", "genres"]:
            self.conn.execute(f"DELETE FROM {t}")
        self.conn.execute("DELETE FROM sqlite_sequence")
        self.conn.commit()

    def fermer(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    db = Cinema("cinema.db")
    tables = db.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print(f"Base initialisée : {db.chemin.resolve()}")
    for t in tables:
        print(f"  - {t['name']}")
    db.fermer()