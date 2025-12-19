"""Unit tests for IP geolocation providers."""

import pytest
from httpx import Response

from app.core.exceptions import (
    IPNotFoundError,
    ProviderUnavailableError,
    RateLimitError,
)
from app.services.ip_providers.ip_api import IPAPIProvider


@pytest.mark.asyncio
class TestIPAPIProvider:
    """Tests for IPAPIProvider."""

    async def test_successful_lookup(self, httpx_mock) -> None:
        """Test successful IP geolocation lookup."""
        # Mock successful response from ip-api.com
        httpx_mock.add_response(
            url="http://ip-api.com/json/8.8.8.8",
            json={
                "status": "success",
                "country": "United States",
                "countryCode": "US",
                "region": "CA",
                "regionName": "California",
                "city": "Mountain View",
                "zip": "94035",
                "lat": 37.386,
                "lon": -122.0838,
                "timezone": "America/Los_Angeles",
                "isp": "Google LLC",
                "org": "Google Public DNS",
                "as": "AS15169 GOOGLE",
                "query": "8.8.8.8",
            },
        )

        provider = IPAPIProvider()
        result = await provider.get_geolocation("8.8.8.8")

        assert str(result.ip) == "8.8.8.8"
        assert result.country == "United States"
        assert result.country_code == "US"
        assert result.region == "California"
        assert result.city == "Mountain View"
        assert result.latitude == 37.386
        assert result.longitude == -122.0838
        assert result.isp == "Google LLC"
        assert result.as_number == "AS15169"
        assert result.as_name == "GOOGLE"

    async def test_ip_not_found(self, httpx_mock) -> None:
        """Test IP not found scenario."""
        # ip-api returns status=fail for invalid IPs
        httpx_mock.add_response(
            url="http://ip-api.com/json/0.0.0.0",
            json={"status": "fail", "message": "reserved range", "query": "0.0.0.0"},
        )

        provider = IPAPIProvider()
        with pytest.raises(IPNotFoundError) as exc_info:
            await provider.get_geolocation("0.0.0.0")

        assert exc_info.value.error_type == "ip_not_found"
        assert exc_info.value.status_code == 404

    async def test_rate_limit_exceeded(self, httpx_mock) -> None:
        """Test rate limit handling."""
        httpx_mock.add_response(
            url="http://ip-api.com/json/8.8.8.8",
            status_code=429,
        )

        provider = IPAPIProvider()
        with pytest.raises(RateLimitError) as exc_info:
            await provider.get_geolocation("8.8.8.8")

        assert exc_info.value.error_type == "rate_limit_exceeded"
        assert exc_info.value.status_code == 429

    async def test_server_error(self, httpx_mock) -> None:
        """Test server error handling."""
        httpx_mock.add_response(
            url="http://ip-api.com/json/8.8.8.8",
            status_code=503,
        )

        provider = IPAPIProvider()
        with pytest.raises(ProviderUnavailableError) as exc_info:
            await provider.get_geolocation("8.8.8.8")

        assert exc_info.value.error_type == "provider_unavailable"
        assert exc_info.value.status_code == 503
        assert "HTTP 503" in exc_info.value.message

    async def test_invalid_json_response(self, httpx_mock) -> None:
        """Test handling of invalid JSON response."""
        httpx_mock.add_response(
            url="http://ip-api.com/json/8.8.8.8",
            content=b"not json",
        )

        provider = IPAPIProvider()
        with pytest.raises(ProviderUnavailableError) as exc_info:
            await provider.get_geolocation("8.8.8.8")

        assert "Invalid JSON response" in exc_info.value.message

    async def test_network_timeout(self, httpx_mock) -> None:
        """Test network timeout handling."""
        httpx_mock.add_exception(
            Exception("Timeout"),
            url="http://ip-api.com/json/8.8.8.8",
        )

        provider = IPAPIProvider()
        with pytest.raises(ProviderUnavailableError) as exc_info:
            await provider.get_geolocation("8.8.8.8")

        assert "Unexpected error" in exc_info.value.message

    async def test_check_health_success(self, httpx_mock) -> None:
        """Test successful health check."""
        httpx_mock.add_response(
            url="http://ip-api.com/json/8.8.8.8",
            json={"status": "success"},
        )

        provider = IPAPIProvider()
        is_healthy = await provider.check_health()

        assert is_healthy is True

    async def test_check_health_failure(self, httpx_mock) -> None:
        """Test failed health check."""
        httpx_mock.add_exception(
            Exception("Network error"),
            url="http://ip-api.com/json/8.8.8.8",
        )

        provider = IPAPIProvider()
        is_healthy = await provider.check_health()

        assert is_healthy is False

    async def test_provider_name(self) -> None:
        """Test provider name property."""
        provider = IPAPIProvider()
        assert provider.name == "ip-api.com"

    async def test_missing_as_field(self, httpx_mock) -> None:
        """Test handling of missing AS field."""
        httpx_mock.add_response(
            url="http://ip-api.com/json/1.1.1.1",
            json={
                "status": "success",
                "country": "Australia",
                "countryCode": "AU",
                "region": "QLD",
                "regionName": "Queensland",
                "city": "Brisbane",
                "zip": "",
                "lat": -27.4678,
                "lon": 153.0281,
                "timezone": "Australia/Brisbane",
                "isp": "Cloudflare",
                "org": "APNIC Research",
                "query": "1.1.1.1",
                # AS field missing
            },
        )

        provider = IPAPIProvider()
        result = await provider.get_geolocation("1.1.1.1")

        assert result.as_number == ""
        assert result.as_name == ""
