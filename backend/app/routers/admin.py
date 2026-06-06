"""
routers/admin.py
----------------
Endpoints réservés à l'administrateur (toi), protégés par get_admin.

  GET /admin/utilisateurs   → liste des comptes (emails, pseudos, nb de films)
                              SANS aucun mot de passe — juste de quoi vérifier
                              que les comptes existent et que les données sont
                              bien rattachées à chacun.
  GET /admin/export         → export COMPLET de toutes les données par
                              utilisateur (films vus, notes, pas vus), en JSON,
                              destiné à être téléchargé pour le moteur de reco.

Note sécurité : les mots de passe ne sont jamais exposés (ils sont hachés et
irréversibles). On expose seulement emails, pseudos et données de films.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_admin
from app.models.user import User
from app.models.user_film import UserFilm
from app.models.film import Film

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/utilisateurs")
def liste_utilisateurs(db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """Aperçu des comptes : pour vérifier qui existe et combien de films chacun
    a enregistrés. Aucun mot de passe (même haché) n'est renvoyé."""
    users = db.query(User).order_by(User.cree_le).all()
    out = []
    for u in users:
        nb_total = db.query(UserFilm).filter(UserFilm.user_id == u.id).count()
        nb_vus = db.query(UserFilm).filter(
            UserFilm.user_id == u.id, UserFilm.vu == True  # noqa: E712
        ).count()
        out.append({
            "id": u.id,
            "email": u.email,
            "pseudo": u.pseudo,
            "est_admin": u.est_admin,
            "cree_le": u.cree_le,
            "films_total": nb_total,
            "films_vus": nb_vus,
        })
    return out


@router.get("/export")
def exporter_tout(db: Session = Depends(get_db), admin: User = Depends(get_admin)):
    """Export complet, structuré par utilisateur, de toutes les données de
    films. Format JSON prêt à alimenter un moteur de recommandations.

    Pour chaque utilisateur : ses films, avec pour chacun le titre, l'année,
    les genres, le statut (vu / pas vu), la note, la date de visionnage.
    """
    users = db.query(User).order_by(User.id).all()
    export = []
    for u in users:
        lignes = (
            db.query(UserFilm, Film)
            .join(Film, UserFilm.film_id == Film.id)
            .filter(UserFilm.user_id == u.id)
            .all()
        )
        films = []
        for uf, film in lignes:
            films.append({
                "film_id": film.id,
                "tmdb_id": film.tmdb_id,
                "titre": film.titre_francais or film.titre_original,
                "annee": film.annee,
                "genres": [g.nom for g in film.genres],
                "pays": [p.nom for p in film.pays],
                "note_public": film.note_public,
                "vu": uf.vu,
                "ma_note": uf.note,
                "urgence": uf.urgence,
                "vu_le": uf.vu_le.isoformat() if uf.vu_le else None,
            })
        export.append({
            "user_id": u.id,
            "email": u.email,
            "pseudo": u.pseudo,
            "nb_films": len(films),
            "films": films,
        })
    return {"utilisateurs": export}
