"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import geolocation

# Create API v1 router
router = APIRouter()

# Include endpoint routers
router.include_router(geolocation.router, tags=["geolocation"])
