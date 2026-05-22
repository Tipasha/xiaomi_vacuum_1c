"""MIoT device class for MIoT protocol devices."""
import logging
from dataclasses import fields as dataclass_fields

from .device import Device
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


class MiotDevice(Device):
    """Device communicating via MIoT protocol (get_properties/set_properties)."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

    def get_properties_for_dataclass(self, cls):
        """Query device properties and fill a dataclass instance."""
        dc_fields = {f.name: f for f in dataclass_fields(cls)}
        property_mapping = {}

        for field_name, fld in dc_fields.items():
            meta = fld.metadata
            if "piid" not in meta:
                continue
            piid = meta["piid"]
            siid = meta.get("siid", getattr(cls, "_siid", None))
            if siid is None:
                raise DeviceException(
                    f"No siid defined for {field_name} or for class {cls}"
                )
            property_mapping[field_name] = {"siid": siid, "piid": piid}

        response = {
            prop["did"]: prop["value"] if prop["code"] == 0 else None
            for prop in self.get_properties_for_mapping(
                property_mapping,
                max_properties=getattr(cls, "_max_properties", 15),
            )
        }

        return cls(**response)

    def set_property(self, **kwargs):
        """Set properties using the device-specific mapping."""
        mapping = getattr(self, "_MAPPING", None)
        if mapping is None:
            raise DeviceException("Device class does not have _MAPPING")
        return self.set_properties_from_dataclass(mapping(**kwargs))

    def set_properties_from_dataclass(self, obj):
        """Set properties from a dataclass instance."""
        dc_fields = {f.name: f for f in dataclass_fields(type(obj))}
        properties_to_set = []

        for field_name, fld in dc_fields.items():
            meta = fld.metadata
            if "piid" not in meta:
                continue
            piid = meta["piid"]
            siid = meta.get("siid", getattr(obj, "_siid", None))
            if siid is None:
                raise DeviceException(
                    f"No siid defined for {field_name} or for class {type(obj)}"
                )
            value = getattr(obj, field_name)
            if value is None:
                continue
            properties_to_set.append({
                "siid": siid,
                "piid": piid,
                "did": field_name,
                "value": value,
            })

        if not properties_to_set:
            raise DeviceException("No values to set!")

        _LOGGER.debug("Setting properties: %s", properties_to_set)
        return self.send("set_properties", properties_to_set)

    def get_properties_for_mapping(self, property_mapping, *, max_properties=15):
        """Retrieve raw properties based on mapping."""
        properties = [{"did": k, **v} for k, v in property_mapping.items()]
        return self.get_properties(properties, max_properties=max_properties)
