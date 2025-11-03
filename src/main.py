"""
Point d'entrée de l'application FastAPI.
Configure et démarre le serveur.
"""
from fastapi import FastAPI
from adapters.primary.fastapi.routers import projects_router


# Création de l'application FastAPI
app = FastAPI(
    title="Project Management API",
    description="API de gestion de projets avec architecture hexagonale",
    version="1.0.0"
)

# Enregistrement des routers
app.include_router(projects_router.router)


@app.get("/")
def root():
    """Endpoint racine pour vérifier que l'API fonctionne."""
    return {"message": "API de gestion de projets - Architecture Hexagonale"}


# Point d'entrée pour démarrer le serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
