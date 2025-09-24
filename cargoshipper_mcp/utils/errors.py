"""Custom exception classes for CargoShipper MCP server"""


class CargoShipperError(Exception):
    """Base exception for CargoShipper MCP server"""
    pass


class ValidationError(CargoShipperError):
    """Validation error"""
    pass


class AuthenticationError(CargoShipperError):
    """Authentication error"""
    pass


class ConfigurationError(CargoShipperError):
    """Configuration error"""
    pass


class ServiceUnavailableError(CargoShipperError):
    """Service unavailable error"""
    pass