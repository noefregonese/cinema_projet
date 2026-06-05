# 🎬 Cinéma

Application web de culture cinématographique : catalogue de films (importés depuis
TMDb), gestion personnelle (vu / note / urgence), comptes utilisateurs, et à terme
recommandations boostées à l'IA.

## Architecture

```
cinema/
├── backend/    FastAPI + SQLAlchemy + JWT
├── frontend/   React + Vite + Tailwind + shadcn/ui
└── scripts/    imports TMDb (ligne de commande)
```

- Le **catalogue** (films, personnes, genres, thèmes, pays) est partagé entre tous.
- Les **données personnelles** (vu, note, urgence) sont propres à chaque utilisateur,
  stockées dans la table `user_films`.

## Démarrage (backend)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # puis remplir les valeurs
uvicorn app.main:app --reload
```

Documentation interactive de l'API : http://localhost:8000/docs

## Démarrage (frontend)

```bash
cd frontend
npm install
npm run dev
```

Interface : http://localhost:5173

## Variables d'environnement

Voir `.env.example`. Ne jamais committer le fichier `.env` réel.
