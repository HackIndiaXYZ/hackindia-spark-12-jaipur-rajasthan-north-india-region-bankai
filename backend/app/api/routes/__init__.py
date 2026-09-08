from fastapi import APIRouter
from app.api.routes import health, network, incidents

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(network.router)
api_router.include_router(incidents.router)
