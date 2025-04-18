"""
Has different types of exceptions
that may aries during the execution
"""

from marshmallow import ValidationError


class InvalidJSONError(ValidationError):
    """Raised when The JSON format is invalid"""


class CommandNotAllowed(Exception):
    """Raised when a command is not allowed."""


class DeviceUnresponsive(Exception):
    """Raised when a device is not responsive."""


class InvalidObsStateError(ValueError):
    """Raised when the device obsState does not
    allow to invoke the command as per SKA state model"""


class ConversionError(ValueError):
    """Raised when the conversion from one unit to another fails."""


class ResourceReassignmentError(Exception):
    """Raised when the resource is already assigned to another subarray"""

    def __init__(self, message: str, resources=None) -> None:
        # super(ResourceReassignmentError, self).__init__(message)
        super().__init__(message)
        self.value = message
        self.resources_reallocation = resources


class AdminModeException(Exception):
    """Custom exception to handle errors related to admin mode."""

    def __init__(self, device_name, command_name: str, message: str):
        super().__init__(message)
        self.command_name = command_name
        self.message = message
        self.device_name = device_name


class ResourceNotPresentError(ValueError):
    """Raised when a resource is requested but not present."""


class SubarrayNotPresentError(ValueError):
    """Raised when a subarray is requested but not present."""


class InvalidReceptorIdError(ValueError):
    """Raised when a requested resource id is invalid."""


class CoefficientError(ValueError):
    """Raised when a requested resource id is invalid."""


class DeviceNameIncorrect(Exception):
    """Raised when a device name is incorrect."""
