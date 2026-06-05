"""
schemas/film.py
---------------
Schémas Pydantic décrivant ce que l'API renvoie/reçoit pour les films.

On distingue :
  - FilmResume / FilmDetail : le film côté CATALOGUE (partagé, objectif).
  - StatutPerso             : les données PERSO d'un utilisateur sur un film.
  - FilmAvecStatut          : la combinaison des deux (film + mon statut),
                              c'est ce qu'on renvoie dans « mes films ».
  - StatutUpdate            : ce que le client envoie pour marquer vu/noter.
"""

from datetime import datetime
from pydantic import BaseModel, Field


# ─── Vocabulaire (sortie simple) ─────────────────────────────────────────────

class NomSeul(BaseModel):
    """Un genre, pays ou thème : juste son nom (et id)."""
    id: int
    nom: str
    model_config = {"from_attributes": True}


class PersonneResume(BaseModel):
    id: int
    nom_complet: str
    model_config = {"from_attributes": True}


# ─── Film côté catalogue ─────────────────────────────────────────────────────

class FilmResume(BaseModel):
    """Version légère pour les listes."""
    id: int
    titre_francais: str | None
    titre_original: str | None
    annee: int | None
    affiche: str | None
    note_public: float | None
    model_config = {"from_attributes": True}


class FilmDetail(FilmResume):
    """Version complète pour la fiche d'un film."""
    duree: int | None
    resume: str | None
    genres: list[NomSeul] = []
    pays: list[NomSeul] = []
    themes: list[NomSeul] = []
    realisateurs: list[PersonneResume] = []
    model_config = {"from_attributes": True}


# ─── Données personnelles ────────────────────────────────────────────────────

class StatutPerso(BaseModel):
    """Le statut d'un utilisateur sur un film."""
    vu: bool = False
    note: float | None = None
    urgence: int = 0
    vu_le: datetime | None = None
    model_config = {"from_attributes": True}


class StatutUpdate(BaseModel):
    """Ce que le client envoie pour mettre à jour son statut sur un film.
    Tous les champs sont optionnels : on ne modifie que ce qui est fourni."""
    vu: bool | None = None
    note: float | None = Field(default=None, ge=0, le=10)
    urgence: int | None = Field(default=None, ge=0)


class FilmAvecStatut(BaseModel):
    """Un film du catalogue + le statut perso de l'utilisateur connecté."""
    film: FilmResume
    statut: StatutPerso
