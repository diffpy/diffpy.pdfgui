"""API v1 router."""
from fastapi import APIRouter
from .endpoints import auth, projects, fittings, phases, datasets, files

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(fittings.router, prefix="/fittings", tags=["fittings"])
api_router.include_router(phases.router, prefix="/phases", tags=["phases"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
