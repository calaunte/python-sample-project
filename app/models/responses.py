"""Pydantic response models for API endpoints."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class GeolocationResponse(BaseModel):
    """Geolocation information for an IP address."""

    ip: IPvAnyAddress
    country: str
    country_code: str
    region: str
    region_code: str
    city: str
    zip_code: str | None = None
    latitude: float
    longitude: float
    timezone: str
    isp: str
    organization: str
    as_number: str
    as_name: str

    model_config = ConfigDict(
        json_schema_extra={
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
    )


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    provider: str
    provider_status: Literal["available", "unavailable"]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "provider": "ip-api.com",
                "provider_status": "available",
            }
        }
    )
