"""Exception classes for miio communication."""


class DeviceException(Exception):
    """Exception wrapping any communication errors with the device."""


class DeviceError(DeviceException):
    """Exception communicating an error delivered by the target device."""

    def __init__(self, error):
        self.code = error.get("code")
        self.message = error.get("message")
        super().__init__(self.message)


class RecoverableError(DeviceError):
    """Recoverable error delivered by the target device."""
