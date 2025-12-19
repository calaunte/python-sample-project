"""Geolocation service orchestration layer."""

from app.core.validators import validate_ip_address
from app.models.responses import GeolocationResponse
from app.services.ip_providers.base import IPGeolocationProvider
from app.services.ip_providers.ip_api import IPAPIProvider


class GeolocationService:
    """Service for IP geolocation lookup with validation and provider orchestration."""

    def __init__(self, provider: IPGeolocationProvider | None = None) -> None:
        """Initialize geolocation service.

        Args:
            provider: IP geolocation provider (defaults to IPAPIProvider)
        """
        self.provider = provider or IPAPIProvider()

    async def geolocate_ip(self, ip: str) -> GeolocationResponse:
        """Get geolocation data for an IP address.

        Args:
            ip: IP address to geolocate

        Returns:
            Geolocation data

        Raises:
            InvalidIPError: If IP format is invalid
            PrivateIPError: If IP is private/reserved
            IPNotFoundError: If IP is not found
            RateLimitError: If rate limit is exceeded
            ProviderUnavailableError: If provider is unavailable
        """
        # Validate IP address (raises InvalidIPError or PrivateIPError)
        validate_ip_address(ip)

        # Fetch geolocation data from provider
        return await self.provider.get_geolocation(ip)

    async def check_provider_health(self) -> bool:
        """Check if the geolocation provider is available.

        Returns:
            True if provider is healthy, False otherwise
        """
        return await self.provider.check_health()

    @property
    def provider_name(self) -> str:
        """Get the current provider name.

        Returns:
            Provider name
        """
        return self.provider.name
