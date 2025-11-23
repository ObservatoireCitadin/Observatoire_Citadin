## Observatoire Citadin - Frontend (Streamlit)

Frontend minimal en Streamlit pour interagir avec l'API du backend (FastAPI).

### Prérequis
- Python 3.10+
- Backend disponible (par défaut `http://localhost:8000`)

### Installation

```bash
cd frontend_test
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optionnel: créer un fichier `.env` dans `frontend_test/`:
```bash
BACKEND_BASE_URL=http://localhost:8000
```

### Lancement

```bash
streamlit run app.py
```

Dans la barre latérale, vous pouvez ajuster l'URL du backend.  
Fonctionnalités:
- Health: ping `GET /api/v1/health`
- Indicateurs: liste via `GET /api/v1/indicators?city_id=&type=`
- Indice ATMO: via `GET /api/v1/atmo/indices?code_zone=&date=&date_historique=`

### Dépannage
- Erreur « Connection refused »: assurez-vous que le backend tourne (`uvicorn app.main:app --reload`) et que l'URL saisie dans la barre latérale pointe vers la bonne adresse (ex: `http://localhost:8000`).
- Cliquez sur « Tester la connexion backend » dans la barre latérale pour vérifier rapidement l'état du backend (`/api/v1/health`).
- Sous WSL2/Docker, utilisez l'IP/port atteignable depuis l'environnement où tourne Streamlit.


