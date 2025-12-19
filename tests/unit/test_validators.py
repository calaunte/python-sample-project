"""Unit tests for IP validation utilities."""

import ipaddress

import pytest

from app.core.exceptions import InvalidIPError, PrivateIPError
from app.core.validators import is_valid_public_ipv4, validate_ip_address


class TestValidateIPAddress:
    """Tests for validate_ip_address function."""

    def test_valid_public_ipv4(self) -> None:
        """Test validation of valid public IPv4 addresses."""
        # Google DNS
        ip = validate_ip_address("8.8.8.8")
        assert isinstance(ip, ipaddress.IPv4Address)
        assert str(ip) == "8.8.8.8"

        # Cloudflare DNS
        ip = validate_ip_address("1.1.1.1")
        assert str(ip) == "1.1.1.1"

    def test_invalid_ip_format(self) -> None:
        """Test validation of invalid IP formats."""
        with pytest.raises(InvalidIPError) as exc_info:
            validate_ip_address("not-an-ip")
        assert exc_info.value.error_type == "invalid_ip"
        assert exc_info.value.status_code == 400

        with pytest.raises(InvalidIPError):
            validate_ip_address("256.1.1.1")

        with pytest.raises(InvalidIPError):
            validate_ip_address("1.1.1")

        with pytest.raises(InvalidIPError):
            validate_ip_address("")

    def test_ipv6_rejected(self) -> None:
        """Test that IPv6 addresses are rejected."""
        with pytest.raises(InvalidIPError):
            validate_ip_address("2001:4860:4860::8888")

    def test_localhost_rejected(self) -> None:
        """Test that localhost is rejected."""
        with pytest.raises(PrivateIPError) as exc_info:
            validate_ip_address("127.0.0.1")
        assert exc_info.value.error_type == "private_ip"
        assert exc_info.value.status_code == 422

    def test_private_ip_ranges_rejected(self) -> None:
        """Test that private IP ranges are rejected."""
        private_ips = [
            "10.0.0.1",
            "10.255.255.255",
            "172.16.0.1",
            "172.31.255.255",
            "192.168.0.1",
            "192.168.255.255",
        ]

        for ip in private_ips:
            with pytest.raises(PrivateIPError):
                validate_ip_address(ip)

    def test_reserved_ips_rejected(self) -> None:
        """Test that reserved IPs are rejected."""
        with pytest.raises(PrivateIPError):
            validate_ip_address("0.0.0.0")

        with pytest.raises(PrivateIPError):
            validate_ip_address("255.255.255.255")

    def test_multicast_rejected(self) -> None:
        """Test that multicast IPs are rejected."""
        with pytest.raises(PrivateIPError):
            validate_ip_address("224.0.0.1")

    def test_link_local_rejected(self) -> None:
        """Test that link-local IPs are rejected."""
        with pytest.raises(PrivateIPError):
            validate_ip_address("169.254.0.1")


class TestIsValidPublicIPv4:
    """Tests for is_valid_public_ipv4 function."""

    def test_valid_public_ips(self) -> None:
        """Test that valid public IPs return True."""
        assert is_valid_public_ipv4("8.8.8.8") is True
        assert is_valid_public_ipv4("1.1.1.1") is True
        assert is_valid_public_ipv4("93.184.216.34") is True  # example.com

    def test_invalid_ips(self) -> None:
        """Test that invalid IPs return False."""
        assert is_valid_public_ipv4("not-an-ip") is False
        assert is_valid_public_ipv4("256.1.1.1") is False
        assert is_valid_public_ipv4("") is False

    def test_private_ips(self) -> None:
        """Test that private IPs return False."""
        assert is_valid_public_ipv4("127.0.0.1") is False
        assert is_valid_public_ipv4("10.0.0.1") is False
        assert is_valid_public_ipv4("192.168.1.1") is False
        assert is_valid_public_ipv4("0.0.0.0") is False
