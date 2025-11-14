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
GEODAIR_API_BASE_URL=https://www.geodair.fr
GEODAIR_API_KEY=
ATMO_API_BASE_URL=https://admindata.atmo-france.org
ATMO_API_KEY=
ATMO_USERNAME=
ATMO_PASSWORD=
```

### Lancer le serveur

```bash
uvicorn app.main:app --reload
```

- Racine: `GET /` -> message de bienvenue
- Healthcheck: `GET /api/v1/health` -> `{ "status": "ok" }`
- Indicateurs: `GET /api/v1/indicators?city_id=<id>&type=<type>`
- Qualité de l'air (Geod'air, proxy): `GET /api/v1/air-quality?pollutant_code=<code>&start=<iso>&end=<iso>&station=<code>`
  - Voir la documentation Geod'air pour les codes polluants et les bonnes pratiques d'appel [`https://www.geodair.fr/donnees/api`](https://www.geodair.fr/donnees/api).

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
│   │   ├── geodair_client.py
│   │   ├── atmo_client.py
│   │   └── run_atmo_indices.py
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

### Script ETL ATMO (indices)

Une CLI simple est disponible pour appeler l'endpoint `data/indices/atmo` via le client:

```bash
cd backend
python -m app.etl.run_atmo_indices --code_zone 75056 --date 2025-11-14
# ou historique
python -m app.etl.run_atmo_indices --code_zone 75056 --date_historique 2024-11-14
```

Le script s'appuie sur les variables d'environnement: `ATMO_API_BASE_URL`, `ATMO_USERNAME`, `ATMO_PASSWORD`.  
Documentation: [`https://admindata.atmo-france.org/api/doc/v2#/`](https://admindata.atmo-france.org/api/doc/v2#/)


