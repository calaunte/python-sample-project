"""Singleton HTTP client for external API calls."""

import httpx


class HTTPClient:
    """Singleton HTTP client with connection pooling."""

    _client: httpx.AsyncClient | None = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        """Get or create the singleton HTTP client.

        Returns:
            Shared httpx.AsyncClient instance
        """
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(5.0),  # 5 second timeout
                follow_redirects=True,
            )
        return cls._client

    @classmethod
    async def close_client(cls) -> None:
        """Close the HTTP client and clean up resources."""
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None
