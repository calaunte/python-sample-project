"""Abstract base class for IP geolocation providers."""

from abc import ABC, abstractmethod

from app.models.responses import GeolocationResponse


class IPGeolocationProvider(ABC):
    """Abstract interface for IP geolocation providers."""

    @abstractmethod
    async def get_geolocation(self, ip: str) -> GeolocationResponse:
        """Fetch geolocation data for an IP address.

        Args:
            ip: IP address to lookup

        Returns:
            Geolocation data

        Raises:
            IPNotFoundError: If IP is not found
            RateLimitError: If rate limit is exceeded
            ProviderUnavailableError: If provider is unavailable
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check if the provider is available.

        Returns:
            True if provider is healthy, False otherwise
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name.

        Returns:
            Provider name
        """
        pass
