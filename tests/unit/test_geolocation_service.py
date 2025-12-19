"""Unit tests for geolocation service."""

from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import InvalidIPError, PrivateIPError
from app.models.responses import GeolocationResponse
from app.services.geolocation import GeolocationService
from app.services.ip_providers.base import IPGeolocationProvider


class MockProvider(IPGeolocationProvider):
    """Mock provider for testing."""

    def __init__(self) -> None:
        """Initialize mock provider."""
        self.get_geolocation_mock = AsyncMock()
        self.check_health_mock = AsyncMock(return_value=True)

    async def get_geolocation(self, ip: str) -> GeolocationResponse:
        """Mock get_geolocation."""
        return await self.get_geolocation_mock(ip)

    async def check_health(self) -> bool:
        """Mock check_health."""
        return await self.check_health_mock()

    @property
    def name(self) -> str:
        """Mock provider name."""
        return "mock-provider"


@pytest.mark.asyncio
class TestGeolocationService:
    """Tests for GeolocationService."""

    async def test_successful_geolocation(self) -> None:
        """Test successful IP geolocation."""
        mock_provider = MockProvider()
        mock_response = GeolocationResponse(
            ip="8.8.8.8",
            country="United States",
            country_code="US",
            region="California",
            region_code="CA",
            city="Mountain View",
            zip_code="94035",
            latitude=37.386,
            longitude=-122.0838,
            timezone="America/Los_Angeles",
            isp="Google LLC",
            organization="Google Public DNS",
            as_number="AS15169",
            as_name="GOOGLE",
        )
        mock_provider.get_geolocation_mock.return_value = mock_response

        service = GeolocationService(provider=mock_provider)
        result = await service.geolocate_ip("8.8.8.8")

        assert result == mock_response
        mock_provider.get_geolocation_mock.assert_called_once_with("8.8.8.8")

    async def test_invalid_ip_format(self) -> None:
        """Test that invalid IP format is rejected."""
        mock_provider = MockProvider()
        service = GeolocationService(provider=mock_provider)

        with pytest.raises(InvalidIPError):
            await service.geolocate_ip("not-an-ip")

        # Provider should not be called for invalid IP
        mock_provider.get_geolocation_mock.assert_not_called()

    async def test_private_ip_rejected(self) -> None:
        """Test that private IPs are rejected."""
        mock_provider = MockProvider()
        service = GeolocationService(provider=mock_provider)

        with pytest.raises(PrivateIPError):
            await service.geolocate_ip("192.168.1.1")

        # Provider should not be called for private IP
        mock_provider.get_geolocation_mock.assert_not_called()

    async def test_localhost_rejected(self) -> None:
        """Test that localhost is rejected."""
        mock_provider = MockProvider()
        service = GeolocationService(provider=mock_provider)

        with pytest.raises(PrivateIPError):
            await service.geolocate_ip("127.0.0.1")

        mock_provider.get_geolocation_mock.assert_not_called()

    async def test_check_provider_health(self) -> None:
        """Test provider health check."""
        mock_provider = MockProvider()
        mock_provider.check_health_mock.return_value = True

        service = GeolocationService(provider=mock_provider)
        is_healthy = await service.check_provider_health()

        assert is_healthy is True
        mock_provider.check_health_mock.assert_called_once()

    async def test_provider_name(self) -> None:
        """Test getting provider name."""
        mock_provider = MockProvider()
        service = GeolocationService(provider=mock_provider)

        assert service.provider_name == "mock-provider"

    async def test_default_provider(self) -> None:
        """Test that default provider is IPAPIProvider."""
        service = GeolocationService()
        assert service.provider_name == "ip-api.com"
