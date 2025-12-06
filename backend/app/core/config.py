from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv
import os


class Settings(BaseModel):
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "observatoire_citadin"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    GEODAIR_API_BASE_URL: str = "https://www.geodair.fr"
    GEODAIR_API_KEY: str = ""
    ATMO_API_BASE_URL: str = "https://admindata.atmo-france.org"
    ATMO_API_KEY: str = ""
    ATMO_USERNAME: str = ""
    ATMO_PASSWORD: str = ""
    SDES_BASE_URL_API: str = "https://data.statistiques.developpement-durable.gouv.fr:443/dido/api/v1"

    @property
    def sqlalchemy_database_uri(self) -> str:
        user = self.POSTGRES_USER
        password = self.POSTGRES_PASSWORD
        host = self.POSTGRES_HOST
        port = self.POSTGRES_PORT
        db = self.POSTGRES_DB
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


@lru_cache()
def get_settings() -> Settings:
    load_dotenv(override=False)
    return Settings(
        POSTGRES_HOST=os.getenv("POSTGRES_HOST", Settings().POSTGRES_HOST),
        POSTGRES_PORT=int(os.getenv("POSTGRES_PORT", Settings().POSTGRES_PORT)),
        POSTGRES_DB=os.getenv("POSTGRES_DB", Settings().POSTGRES_DB),
        POSTGRES_USER=os.getenv("POSTGRES_USER", Settings().POSTGRES_USER),
        POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", Settings().POSTGRES_PASSWORD),
        GEODAIR_API_BASE_URL=os.getenv("GEODAIR_API_BASE_URL", Settings().GEODAIR_API_BASE_URL),
        GEODAIR_API_KEY=os.getenv("GEODAIR_API_KEY", Settings().GEODAIR_API_KEY),
        ATMO_API_BASE_URL=os.getenv("ATMO_API_BASE_URL", Settings().ATMO_API_BASE_URL),
        ATMO_API_KEY=os.getenv("ATMO_API_KEY", Settings().ATMO_API_KEY),
        ATMO_USERNAME=os.getenv("ATMO_USERNAME", Settings().ATMO_USERNAME),
        ATMO_PASSWORD=os.getenv("ATMO_PASSWORD", Settings().ATMO_PASSWORD),
    )


