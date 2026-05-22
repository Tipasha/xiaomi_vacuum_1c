"""Base device class for miIO protocol devices."""
import logging
from typing import Any, Optional

from .exceptions import DeviceException
from .miioprotocol import MiIOProtocol

_LOGGER = logging.getLogger(__name__)


class Device:
    """Base class for miIO protocol devices."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        self.ip = ip
        self.token = token
        self._protocol = MiIOProtocol(ip, token, start_id, debug, lazy_discover)

    def send(self, command: str, parameters: Any = None, retry_count: int = 3) -> Any:
        """Send a command to the device."""
        return self._protocol.send(command, parameters, retry_count)

    def get_properties(self, properties, *, max_properties=None):
        """Request properties in slices based on given max_properties."""
        _props = properties.copy()
        values = []
        while _props:
            try:
                properties_to_request = _props[:max_properties]
                values.extend(self.send("get_properties", properties_to_request))
            except DeviceException:
                _LOGGER.error("Unable to request properties %s", properties_to_request)
            if max_properties is None:
                break
            _props[:] = _props[max_properties:]

        return values
