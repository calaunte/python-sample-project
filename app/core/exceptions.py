"""Custom exception classes for geolocation service."""


class GeolocationError(Exception):
    """Base exception for geolocation errors."""

    def __init__(self, message: str, error_type: str, status_code: int) -> None:
        """Initialize geolocation error.

        Args:
            message: Human-readable error message
            error_type: Machine-readable error type code
            status_code: HTTP status code
        """
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        super().__init__(message)


class InvalidIPError(GeolocationError):
    """Raised when IP address is invalid."""

    def __init__(self, ip: str) -> None:
        """Initialize invalid IP error.

        Args:
            ip: The invalid IP address
        """
        super().__init__(f"Invalid IPv4 address: {ip}", "invalid_ip", 400)


class PrivateIPError(GeolocationError):
    """Raised when IP is private/reserved."""

    def __init__(self, ip: str) -> None:
        """Initialize private IP error.

        Args:
            ip: The private/reserved IP address
        """
        super().__init__(
            f"Cannot geolocate private/reserved IP: {ip}", "private_ip", 422
        )


class IPNotFoundError(GeolocationError):
    """Raised when IP is not found in geolocation database."""

    def __init__(self, ip: str) -> None:
        """Initialize IP not found error.

        Args:
            ip: The IP address that was not found
        """
        super().__init__(
            f"Geolocation data not found for IP: {ip}", "ip_not_found", 404
        )


class RateLimitError(GeolocationError):
    """Raised when provider rate limit is exceeded."""

    def __init__(self, provider: str) -> None:
        """Initialize rate limit error.

        Args:
            provider: The provider name
        """
        super().__init__(
            f"Rate limit exceeded for provider: {provider}",
            "rate_limit_exceeded",
            429,
        )


class ProviderUnavailableError(GeolocationError):
    """Raised when provider API is unavailable."""

    def __init__(self, provider: str, reason: str) -> None:
        """Initialize provider unavailable error.

        Args:
            provider: The provider name
            reason: Reason for unavailability
        """
        super().__init__(
            f"Geolocation provider {provider} is unavailable: {reason}",
            "provider_unavailable",
            503,
        )


class ClientIPDetectionError(GeolocationError):
    """Raised when client IP cannot be determined."""

    def __init__(self) -> None:
        """Initialize client IP detection error."""
        super().__init__(
            "Unable to determine client IP address",
            "client_ip_detection_failed",
            400,
        )
