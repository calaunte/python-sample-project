"""Integration tests for geolocation API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestGeolocateIPEndpoint:
    """Tests for /api/v1/geolocate/{ip} endpoint."""

    async def test_successful_lookup(self, client: AsyncClient, httpx_mock) -> None:
        """Test successful IP geolocation lookup."""
        # Mock ip-api.com response
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

        response = await client.get("/api/v1/geolocate/8.8.8.8")

        assert response.status_code == 200
        data = response.json()
        assert data["ip"] == "8.8.8.8"
        assert data["country"] == "United States"
        assert data["country_code"] == "US"
        assert data["city"] == "Mountain View"
        assert data["latitude"] == 37.386
        assert data["longitude"] == -122.0838

    async def test_invalid_ip_format(self, client: AsyncClient) -> None:
        """Test invalid IP address format returns 400."""
        response = await client.get("/api/v1/geolocate/not-an-ip")

        assert response.status_code == 400
        data = response.json()
        assert data["error"]["type"] == "invalid_ip"
        assert "Invalid IPv4 address" in data["error"]["message"]

    async def test_private_ip_rejected(self, client: AsyncClient) -> None:
        """Test private IP address returns 422."""
        response = await client.get("/api/v1/geolocate/192.168.1.1")

        assert response.status_code == 422
        data = response.json()
        assert data["error"]["type"] == "private_ip"
        assert "private/reserved" in data["error"]["message"]

    async def test_localhost_rejected(self, client: AsyncClient) -> None:
        """Test localhost IP returns 422."""
        response = await client.get("/api/v1/geolocate/127.0.0.1")

        assert response.status_code == 422
        data = response.json()
        assert data["error"]["type"] == "private_ip"

    async def test_reserved_ip_rejected(self, client: AsyncClient) -> None:
        """Test reserved IP address returns 422."""
        # 0.0.0.0 is reserved, so it will fail validation before hitting the provider
        response = await client.get("/api/v1/geolocate/0.0.0.0")

        assert response.status_code == 422
        assert response.json()["error"]["type"] == "private_ip"

    async def test_rate_limit_exceeded(self, client: AsyncClient, httpx_mock) -> None:
        """Test rate limit exceeded returns 429."""
        httpx_mock.add_response(
            url="http://ip-api.com/json/8.8.8.8",
            status_code=429,
        )

        response = await client.get("/api/v1/geolocate/8.8.8.8")

        assert response.status_code == 429
        data = response.json()
        assert data["error"]["type"] == "rate_limit_exceeded"

    async def test_provider_unavailable(self, client: AsyncClient, httpx_mock) -> None:
        """Test provider unavailable returns 503."""
        httpx_mock.add_response(
            url="http://ip-api.com/json/8.8.8.8",
            status_code=503,
        )

        response = await client.get("/api/v1/geolocate/8.8.8.8")

        assert response.status_code == 503
        data = response.json()
        assert data["error"]["type"] == "provider_unavailable"


@pytest.mark.asyncio
class TestGeolocateClientIPEndpoint:
    """Tests for /api/v1/geolocate endpoint (client IP detection)."""

    async def test_client_ip_with_x_forwarded_for(
        self, client: AsyncClient, httpx_mock
    ) -> None:
        """Test client IP detection with X-Forwarded-For header."""
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

        response = await client.get(
            "/api/v1/geolocate", headers={"X-Forwarded-For": "8.8.8.8"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ip"] == "8.8.8.8"

    async def test_client_ip_with_multiple_forwarded_ips(
        self, client: AsyncClient, httpx_mock
    ) -> None:
        """Test X-Forwarded-For with comma-separated IPs (takes first)."""
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

        response = await client.get(
            "/api/v1/geolocate",
            headers={"X-Forwarded-For": "8.8.8.8, 192.168.1.1, 10.0.0.1"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ip"] == "8.8.8.8"

    async def test_client_ip_with_x_real_ip(
        self, client: AsyncClient, httpx_mock
    ) -> None:
        """Test client IP detection with X-Real-IP header."""
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
                "as": "AS13335 Cloudflare",
                "query": "1.1.1.1",
            },
        )

        response = await client.get(
            "/api/v1/geolocate", headers={"X-Real-IP": "1.1.1.1"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ip"] == "1.1.1.1"

    async def test_client_ip_private_rejected(self, client: AsyncClient) -> None:
        """Test that private client IP is rejected."""
        response = await client.get(
            "/api/v1/geolocate", headers={"X-Forwarded-For": "192.168.1.1"}
        )

        assert response.status_code == 422
        data = response.json()
        assert data["error"]["type"] == "private_ip"


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for /health endpoint."""

    async def test_health_check(self, client: AsyncClient) -> None:
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
