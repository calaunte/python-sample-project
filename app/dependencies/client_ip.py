"""FastAPI dependency for extracting client IP address."""

from fastapi import Request

from app.core.exceptions import ClientIPDetectionError


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request headers.

    Tries headers in this order:
    1. X-Forwarded-For (proxy/load balancer)
    2. X-Real-IP (alternative proxy header)
    3. request.client.host (direct connection)

    Args:
        request: FastAPI request object

    Returns:
        Client IP address

    Raises:
        ClientIPDetectionError: If unable to determine client IP
    """
    # Try X-Forwarded-For header (most common for proxied requests)
    if forwarded := request.headers.get("X-Forwarded-For"):
        # X-Forwarded-For can be comma-separated, take first IP
        return forwarded.split(",")[0].strip()

    # Try X-Real-IP header (alternative proxy header)
    if real_ip := request.headers.get("X-Real-IP"):
        return real_ip.strip()

    # Fallback to direct connection
    if request.client and request.client.host:
        return request.client.host

    # Unable to determine client IP
    raise ClientIPDetectionError()
