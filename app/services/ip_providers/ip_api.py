"""ip-api.com geolocation provider implementation."""

import httpx

from app.core.exceptions import (
    IPNotFoundError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.core.http_client import HTTPClient
from app.models.responses import GeolocationResponse
from app.services.ip_providers.base import IPGeolocationProvider


class IPAPIProvider(IPGeolocationProvider):
    """ip-api.com geolocation provider.

    API Documentation: https://ip-api.com/docs
    Free tier: 45 requests per minute
    """

    BASE_URL = "http://ip-api.com/json"

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "ip-api.com"

    async def get_geolocation(self, ip: str) -> GeolocationResponse:
        """Fetch geolocation data for an IP address from ip-api.com.

        Args:
            ip: IP address to lookup

        Returns:
            Geolocation data

        Raises:
            IPNotFoundError: If IP is not found
            RateLimitError: If rate limit is exceeded
            ProviderUnavailableError: If provider is unavailable
        """
        client = HTTPClient.get_client()
        url = f"{self.BASE_URL}/{ip}"

        try:
            response = await client.get(url)

            # Handle rate limiting
            if response.status_code == 429:
                raise RateLimitError(self.name)

            # Handle server errors
            if response.status_code >= 500:
                raise ProviderUnavailableError(
                    self.name, f"HTTP {response.status_code}"
                )

            # Parse response
            try:
                data = response.json()
            except Exception as e:
                raise ProviderUnavailableError(
                    self.name, f"Invalid JSON response: {e}"
                ) from e

            # Check if IP lookup was successful
            if data.get("status") == "fail":
                # ip-api returns status=fail for invalid/not found IPs
                raise IPNotFoundError(ip)

            # Map ip-api.com response to our model
            return GeolocationResponse(
                ip=data["query"],
                country=data.get("country", ""),
                country_code=data.get("countryCode", ""),
                region=data.get("regionName", ""),
                region_code=data.get("region", ""),
                city=data.get("city", ""),
                zip_code=data.get("zip"),
                latitude=data.get("lat", 0.0),
                longitude=data.get("lon", 0.0),
                timezone=data.get("timezone", ""),
                isp=data.get("isp", ""),
                organization=data.get("org", ""),
                as_number=data.get("as", "").split()[0] if data.get("as") else "",
                as_name=" ".join(data.get("as", "").split()[1:])
                if data.get("as")
                else "",
            )

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            raise ProviderUnavailableError(
                self.name, f"Network error: {type(e).__name__}"
            ) from e
        except (RateLimitError, IPNotFoundError, ProviderUnavailableError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise ProviderUnavailableError(
                self.name, f"Unexpected error: {type(e).__name__}"
            ) from e

    async def check_health(self) -> bool:
        """Check if ip-api.com is available.

        Returns:
            True if provider is healthy, False otherwise
        """
        client = HTTPClient.get_client()
        try:
            # Use a known public IP (Google DNS) for health check
            response = await client.get(f"{self.BASE_URL}/8.8.8.8", timeout=3.0)
            return response.status_code == 200
        except Exception:
            return False
