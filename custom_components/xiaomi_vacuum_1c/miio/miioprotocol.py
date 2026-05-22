"""miIO protocol transport layer.

Handles UDP communication, handshakes, and message framing.
"""
import codecs
import datetime
import logging
import socket
from typing import Any, List

import construct

from .exceptions import DeviceError, DeviceException, RecoverableError
from .protocol import Message

_LOGGER = logging.getLogger(__name__)


class MiIOProtocol:
    """Low-level miIO UDP protocol handler."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        self.ip = ip
        self.port = 54321
        if token is None:
            token = 32 * "0"
        self.token = bytes.fromhex(token)
        self.debug = debug
        self.lazy_discover = lazy_discover

        self._timeout = 5
        self._discovered = False
        self._device_ts = None
        self.__id = start_id
        self._device_id = None

    def send_handshake(self) -> Message:
        """Send a handshake to discover the device."""
        m = MiIOProtocol.discover(self.ip)
        if m is not None:
            header = m.header.value
            self._device_id = header.device_id
            self._device_ts = header.ts
            self._discovered = True
            if self.debug > 1:
                _LOGGER.debug(m)
            _LOGGER.debug(
                "Discovered %s with ts: %s, token: %s",
                binascii_hexlify(self._device_id),
                self._device_ts,
                codecs.encode(m.checksum, "hex"),
            )
        else:
            _LOGGER.error("Unable to discover the device %s", self.ip)
            raise DeviceException("Unable to discover the device")

        return m

    @staticmethod
    def discover(addr: str = None) -> Any:
        """Scan for devices in the network or discover a specific device."""
        timeout = 5
        is_broadcast = addr is None
        seen_addrs = []
        if is_broadcast:
            addr = "<broadcast>"
            is_broadcast = True
            _LOGGER.info("Sending discovery to %s with timeout of %ss..", addr, timeout)

        helobytes = bytes.fromhex(
            "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        s.sendto(helobytes, (addr, 54321))

        if is_broadcast:
            devices = {}
            while True:
                try:
                    data, recv_addr = s.recvfrom(1024)
                    m = Message.parse(data)
                    if recv_addr[0] not in seen_addrs:
                        _LOGGER.info("  IP %s (ID: %s) - token: %s", recv_addr[0],
                                     codecs.encode(m.header.value.device_id, "hex"),
                                     codecs.encode(m.checksum, "hex"))
                        seen_addrs.append(recv_addr[0])
                        devices[recv_addr[0]] = m
                except socket.timeout:
                    break
                except Exception as ex:
                    _LOGGER.warning("Error reading discover response: %s", ex)
                    break
            return devices
        else:
            try:
                data, recv_addr = s.recvfrom(1024)
                m = Message.parse(data)
                return m
            except socket.timeout:
                raise DeviceException("No response from device %s" % addr)
            except Exception as ex:
                _LOGGER.warning("Error reading response from %s: %s", addr, ex)
                raise DeviceException("Error communicating with device") from ex
            finally:
                s.close()

    def send(self, command: str, parameters: Any = None, retry_count: int = 3) -> Any:
        """Build and send a command to the device."""
        if not self.lazy_discover or not self._discovered:
            self.send_handshake()

        cmd = {"id": self._id, "method": command}
        if parameters is not None:
            cmd["params"] = parameters
        else:
            cmd["params"] = []

        send_ts = self._device_ts + datetime.timedelta(seconds=1)

        header = {
            "length": 0,
            "unknown": 0x00000000,
            "device_id": self._device_id,
            "ts": send_ts,
        }

        msg = {"data": {"value": cmd}, "header": {"value": header}, "checksum": 0}

        m = Message.build(msg, token=self.token)
        _LOGGER.debug("%s:%s >>: %s", self.ip, self.port, cmd)

        if self.debug > 1:
            _LOGGER.debug("send (timeout %s): %s", self._timeout, Message.parse(m, token=self.token))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(self._timeout)

        try:
            s.sendto(m, (self.ip, self.port))
        except OSError as ex:
            _LOGGER.error("Failed to send to %s: %s", self.ip, ex)
            raise DeviceException("Send failed") from ex

        try:
            data, addr = s.recvfrom(1024)
            m = Message.parse(data, token=self.token)
            self._device_ts = m.header.value.ts

            _LOGGER.debug("%s:%s (ts: %s) <<: %s", self.ip, self.port,
                          m.header.value.ts, m.data.value)

            try:
                payload = m.data.value
            except Exception as ex:
                _LOGGER.error("Error getting payload: %s", ex)
                raise DeviceException("Error getting payload") from ex

            if "error" in payload:
                error = payload["error"]
                if "code" in error and error["code"] == -9999:
                    self._discovered = False
                    if retry_count > 0:
                        return self.send(command, parameters, retry_count - 1)
                    raise RecoverableError(error)
                raise DeviceError(error)

            try:
                return payload["result"]
            except KeyError:
                return payload

        except construct.core.ChecksumError as ex:
            raise DeviceException("Got checksum error") from ex
        except socket.timeout:
            _LOGGER.debug("Timeout waiting for response from %s", self.ip)
            if retry_count > 0:
                return self.send(command, parameters, retry_count - 1)
            raise DeviceException("No response from device")
        finally:
            s.close()

    @property
    def _id(self) -> int:
        """Increment and return the sequence id."""
        self.__id += 1
        if self.__id >= 9999:
            self.__id = 1
        return self.__id
