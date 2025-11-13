from fastapi import FastAPI

from app.api.v1 import router as api_v1_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Observatoire Citadin API",
        version="1.0.0",
        description="Backend de l'Observatoire Citadin",
    )

    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/")
    def read_root():
        return {"message": "Observatoire Citadin API"}

    return app


app = create_app()


