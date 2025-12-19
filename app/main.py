"""FastAPI application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1 import router as api_v1_router
from app.core.exceptions import GeolocationError
from app.models.errors import ErrorDetail, ErrorResponse

# Create FastAPI app
app = FastAPI(
    title="IP Geolocation Service",
    description="FastAPI microservice for IP address geolocation lookup",
    version=__version__,
)

# Include API v1 router
app.include_router(api_v1_router.router, prefix="/api/v1")


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


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "version": __version__}
