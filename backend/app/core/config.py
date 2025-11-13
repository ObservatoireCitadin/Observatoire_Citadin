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
    )


