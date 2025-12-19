"""Geolocation API endpoints."""

from fastapi import APIRouter, Depends, Request

from app.dependencies.client_ip import get_client_ip
from app.models.responses import GeolocationResponse
from app.services.geolocation import GeolocationService

router = APIRouter()


@router.get(
    "/geolocate/{ip}",
    response_model=GeolocationResponse,
    summary="Geolocate a specific IP address",
    description="Look up geolocation information for a specific IPv4 address",
    responses={
        200: {
            "description": "Geolocation data found successfully",
            "content": {
                "application/json": {
                    "example": {
                        "ip": "8.8.8.8",
                        "country": "United States",
                        "country_code": "US",
                        "region": "California",
                        "region_code": "CA",
                        "city": "Mountain View",
                        "zip_code": "94035",
                        "latitude": 37.386,
                        "longitude": -122.0838,
                        "timezone": "America/Los_Angeles",
                        "isp": "Google LLC",
                        "organization": "Google Public DNS",
                        "as_number": "AS15169",
                        "as_name": "GOOGLE",
                    }
                }
            },
        },
        400: {"description": "Invalid IP address format"},
        404: {"description": "IP address not found in geolocation database"},
        422: {"description": "Private or reserved IP address"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Geolocation provider unavailable"},
    },
)
async def geolocate_ip(ip: str) -> GeolocationResponse:
    """Look up geolocation for a specific IP address.

    Args:
        ip: IPv4 address to geolocate

    Returns:
        Geolocation data including country, region, city, coordinates, ISP, etc.
    """
    service = GeolocationService()
    return await service.geolocate_ip(ip)


@router.get(
    "/geolocate",
    response_model=GeolocationResponse,
    summary="Geolocate the requesting client's IP address",
    description="Automatically detect and geolocate the client's IP address from request headers",
    responses={
        200: {"description": "Geolocation data found successfully"},
        400: {"description": "Unable to determine client IP or invalid IP format"},
        404: {"description": "IP address not found in geolocation database"},
        422: {"description": "Private or reserved IP address"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Geolocation provider unavailable"},
    },
)
async def geolocate_client_ip(
    request: Request, client_ip: str = Depends(get_client_ip)
) -> GeolocationResponse:
    """Look up geolocation for the requesting client's IP address.

    Automatically detects client IP from request headers (X-Forwarded-For, X-Real-IP)
    or direct connection.

    Args:
        request: FastAPI request object
        client_ip: Client IP address extracted from headers

    Returns:
        Geolocation data for the client's IP address
    """
    service = GeolocationService()
    return await service.geolocate_ip(client_ip)
