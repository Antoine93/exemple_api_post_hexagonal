"""
Point d'entrée de l'application FastAPI.
Configure et démarre le serveur.
"""
from fastapi import FastAPI
from src.adapters.primary.fastapi.routers import projects_router, users_router


# Création de l'application FastAPI
app = FastAPI(
    title="Project & User Management API",
    description="API de gestion de projets et utilisateurs avec architecture hexagonale",
    version="3.0.0"
)

# Enregistrement des routers
app.include_router(projects_router.router)
app.include_router(users_router.router)


@app.get("/")
def root() -> dict[str, str]:
    """Endpoint racine pour vérifier que l'API fonctionne."""
    return {
        "message": "API de gestion de projets et utilisateurs - Architecture Hexagonale",
        "version": "3.0.0",
        "endpoints": {
            "projects": "/api/projects",
            "users": "/api/users",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


# Point d'entrée pour démarrer le serveur
if __name__ == "__main__":
    import hypercorn.run
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:8000"]
    hypercorn.run.run(config)
