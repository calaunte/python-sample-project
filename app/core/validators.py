"""IP address validation utilities."""

import ipaddress

from app.core.exceptions import InvalidIPError, PrivateIPError


def validate_ip_address(ip: str) -> ipaddress.IPv4Address:
    """Validate and parse an IPv4 address.

    Args:
        ip: IP address string to validate

    Returns:
        Parsed IPv4Address object

    Raises:
        InvalidIPError: If IP format is invalid
        PrivateIPError: If IP is private, loopback, or reserved
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError as e:
        raise InvalidIPError(ip) from e

    # Only support IPv4
    if not isinstance(ip_obj, ipaddress.IPv4Address):
        raise InvalidIPError(ip)

    # Check for private/reserved addresses
    if ip_obj.is_private:
        raise PrivateIPError(ip)

    if ip_obj.is_loopback:
        raise PrivateIPError(ip)

    if ip_obj.is_reserved:
        raise PrivateIPError(ip)

    if ip_obj.is_multicast:
        raise PrivateIPError(ip)

    if ip_obj.is_link_local:
        raise PrivateIPError(ip)

    if ip_obj.is_unspecified:
        raise PrivateIPError(ip)

    return ip_obj


def is_valid_public_ipv4(ip: str) -> bool:
    """Check if an IP address is a valid public IPv4 address.

    Args:
        ip: IP address string to check

    Returns:
        True if valid public IPv4, False otherwise
    """
    try:
        validate_ip_address(ip)
        return True
    except (InvalidIPError, PrivateIPError):
        return False
