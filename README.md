## Observatoire Citadin

Application composée d’un backend API (FastAPI) et d’un frontend analytique (Streamlit) pour explorer des indicateurs urbains (ex. qualité de l’air, indicateurs par ville).

### Architecture
- **Backend**: FastAPI (Python), endpoints versionnés sous `/api/v1`.
- **Frontend**: Streamlit, consomme l’API backend.
- **ETL**: scripts clients pour Geod’air / Atmo dans `backend/app/etl/`.

Consultez les détails par composant:
- Backend: `backend/README_BACKEND.md`
- Frontend: `frontend/README_FRONTEND.md`

## Prérequis
- Python 3.10+ (recommandé)
- Accès réseau aux sources de données externes si vous utilisez les clients ETL (Geod’air / Atmo)

## Démarrage rapide

### 1) Lancer l’API (FastAPI)

```bash
cd backend
pyenv virtualenv 3.12.9 obs_cit_back_venv
pyenv local obs_cit_back_venv
pip install -r requirements.txt

# Optionnel: variables d'environnement (voir plus bas et backend/README_BACKEND.md)
# touch .env  # si vous utilisez python-dotenv

uvicorn app.main:app --reload
```

Par défaut, l’API écoute sur `http://localhost:8000` avec:
- Documentation Swagger UI: `http://localhost:8000/docs`
- Racine: `GET /` → message de bienvenue
- API v1: `GET /api/v1/...`

Variables d’environnement courantes (extrait, voir la liste complète dans `backend/README_BACKEND.md`):
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

### 2) Lancer le frontend (Streamlit)

Dans un second terminal:
```bash
cd frontend
pyenv virtualenv 3.12.9 obs_cit_front_venv
pyenv local obs_cit_front_venv
pip install -r requirements.txt

# Optionnel: pointer vers l’API si différent de localhost:8000
# echo "BACKEND_BASE_URL=http://localhost:8000" > .env

streamlit run app.py
```

Le frontend s’ouvre dans le navigateur (port par défaut 8501). Dans la barre latérale, vous pouvez ajuster l’URL du backend et tester la connexion (`/api/v1/health`).

## Développement et ETL
- Les scripts et clients ETL se trouvent sous `backend/app/etl/`.
- Exemple (indices ATMO) depuis `backend/`:
  ```bash
  python -m app.etl.run_atmo_indices --code_zone 75056 --date 2025-11-14
  # ou historique
  python -m app.etl.run_atmo_indices --code_zone 75056 --date_historique 2024-11-14
  ```
- Ces scripts utilisent les variables d’environnement ATMO indiquées plus haut.

## Dépannage
- Si le frontend affiche « Connection refused », vérifiez que l’API tourne bien (`uvicorn app.main:app --reload`) et que `BACKEND_BASE_URL` pointe vers l’adresse atteignable.
- Sous WSL2, assurez-vous d’utiliser une URL/port joignable depuis l’environnement où tourne Streamlit.
- En cas d’erreur 404 côté API, vérifiez que vous ciblez bien les endpoints sous `/api/v1`.

## Structure (aperçu)
```
Observatoire_Citadin/
├── backend/
│   ├── app/
│   │   ├── api/v1/...
│   │   ├── etl/...
│   │   └── main.py
│   ├── requirements.txt
│   └── README_BACKEND.md
└── frontend/
    ├── app.py
    ├── requirements.txt
    └── README_FRONTEND.md
```


