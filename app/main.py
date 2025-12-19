"""FastAPI application entrypoint."""

from typing import Literal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1 import router as api_v1_router
from app.config import settings
from app.core.exceptions import GeolocationError
from app.core.http_client import HTTPClient
from app.models.errors import ErrorDetail, ErrorResponse
from app.models.responses import HealthCheckResponse
from app.services.geolocation import GeolocationService

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="FastAPI microservice for IP address geolocation lookup",
    version=__version__,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Include API v1 router
app.include_router(api_v1_router.router, prefix=settings.api_v1_prefix)


# Global exception handler for GeolocationError
@app.exception_handler(GeolocationError)
async def geolocation_error_handler(
    request: Request, exc: GeolocationError
) -> JSONResponse:
    """Handle geolocation errors with consistent error response format.

    Args:
        request: FastAPI request object
        exc: Geolocation error exception

    Returns:
        JSON error response
    """
    error_response = ErrorResponse(
        error=ErrorDetail(type=exc.error_type, message=exc.message)
    )
    return JSONResponse(
        status_code=exc.status_code, content=error_response.model_dump()
    )


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up resources on shutdown."""
    await HTTPClient.close_client()


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["health"],
    summary="Health check",
    description="Check if the service and provider are available",
)
async def health_check() -> HealthCheckResponse:
    """Health check endpoint.

    Returns:
        Health status including provider availability
    """
    service = GeolocationService()
    provider_available = await service.check_provider_health()

    status: Literal["healthy", "degraded", "unhealthy"]
    if provider_available:
        status = "healthy"
    else:
        status = "degraded"

    return HealthCheckResponse(
        status=status,
        version=__version__,
        provider=service.provider_name,
        provider_status="available" if provider_available else "unavailable",
    )
