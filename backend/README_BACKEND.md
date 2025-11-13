## Observatoire Citadin - Backend (FastAPI)

Backend du projet Observatoire Citadin, basé sur FastAPI, SQLAlchemy et PostgreSQL, avec une structure modulaire et évolutive.

### Installation rapide

1) Cloner le dépôt et se placer dans le dossier backend

```bash
cd backend
```

2) Créer et activer un environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3) Installer les dépendances

```bash
pip install -r requirements.txt
```

### Configuration (.env)

Créer un fichier `.env` à la racine du dossier `backend/` avec les variables suivantes :

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=observatoire_citadin
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### Lancer le serveur

```bash
uvicorn app.main:app --reload
```

- Racine: `GET /` -> message de bienvenue
- Healthcheck: `GET /api/v1/health` -> `{ "status": "ok" }`
- Indicateurs: `GET /api/v1/indicators?city_id=<id>&type=<type>`

### Structure des dossiers

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   └── indicators.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── deps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── city.py
│   │   └── indicator.py
│   ├── etl/
│   │   ├── __init__.py
│   │   └── (scripts à venir)
│   ├── main.py
│   └── __init__.py
├── requirements.txt
├── README_BACKEND.md
└── tests/
    ├── __init__.py
    └── test_health.py
```

### Modèles de données

- City: `id`, `name`, `insee_code`
- Indicator: `id`, `city_id`, `type`, `value`, `date`, `source`

### Notes

- La base de données PostgreSQL n'est pas migrée automatiquement. Créez les tables via un outil de migration (ex. Alembic) ou manuellement selon vos besoins.
- Les scripts ETL doivent être ajoutés dans `app/etl/`.


