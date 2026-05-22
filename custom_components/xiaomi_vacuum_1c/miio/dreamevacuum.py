"""Dreame Vacuum device implementation for Xiaomi Mi Robot Vacuum-Mop 1C (dreame.vacuum.mc1808)."""
import logging
from dataclasses import dataclass, field
from enum import Enum

from .miot_device import MiotDevice

_LOGGER = logging.getLogger(__name__)


class ChargeStatus(Enum):
    Charging = 1
    Not_charging = 2
    Charging2 = 4
    Go_charging = 5


class Error(Enum):
    NoError = 0
    Drop = 1
    Cliff = 2
    Bumper = 3
    Gesture = 4
    Bumper_repeat = 5
    Drop_repeat = 6
    Optical_flow = 7
    No_box = 8
    No_tankbox = 9
    Waterbox_empty = 10
    Box_full = 11
    Brush = 12
    Side_brush = 13
    Fan = 14
    Left_wheel_motor = 15
    Right_wheel_motor = 16
    Turn_suffocate = 17
    Forward_suffocate = 18
    Charger_get = 19
    Battery_low = 20
    Charge_fault = 21
    Battery_percentage = 22
    Heart = 23
    Camera_occlusion = 24
    Camera_fault = 25
    Event_battery = 26
    Forward_looking = 27
    Gyroscope = 28


class VacuumStatus(Enum):
    Sweeping = 1
    Idle = 2
    Paused = 3
    Error = 4
    Go_charging = 5
    Charging = 6


class VacuumSpeed(Enum):
    Silent = 0
    Standard = 1
    Medium = 2
    Turbo = 3


class WaterLevel(Enum):
    Low = 1
    Medium = 2
    High = 3


@dataclass
class DreameStatus:
    """Status container for Dreame Vacuum MC1808 (Xiaomi Mi Robot Vacuum-Mop 1C)."""

    _max_properties = 10

    # siid 2: Battery
    battery: int = field(
        metadata={"siid": 2, "piid": 1, "access": ["read", "notify"]},
        default=None,
    )
    state: int = field(
        metadata={"siid": 2, "piid": 2, "access": ["read", "notify"], "enum": ChargeStatus},
        default=None,
    )

    # siid 3: Robot Cleaner
    error: int = field(
        metadata={"siid": 3, "piid": 1, "access": ["read", "notify"], "enum": Error},
        default=None,
    )
    status: int = field(
        metadata={"siid": 3, "piid": 2, "access": ["read", "notify"], "enum": VacuumStatus},
        default=None,
    )

    # siid 26: Main Cleaning Brush
    brush_left_time: int = field(
        metadata={"siid": 26, "piid": 1, "access": ["read", "notify"]},
        default=None,
    )
    brush_life_level: int = field(
        metadata={"siid": 26, "piid": 2, "access": ["read", "notify"]},
        default=None,
    )

    # siid 27: Filter
    filter_life_level: int = field(
        metadata={"siid": 27, "piid": 1, "access": ["read", "notify"]},
        default=None,
    )
    filter_left_time: int = field(
        metadata={"siid": 27, "piid": 2, "access": ["read", "notify"]},
        default=None,
    )

    # siid 28: Side Cleaning Brush
    brush_left_time2: int = field(
        metadata={"siid": 28, "piid": 1, "access": ["read", "notify"]},
        default=None,
    )
    brush_life_level2: int = field(
        metadata={"siid": 28, "piid": 2, "access": ["read", "notify"]},
        default=None,
    )

    # siid 18: Clean
    operating_mode: int = field(
        metadata={"siid": 18, "piid": 1, "access": ["read", "notify"]},
        default=None,
    )
    area: str = field(
        metadata={"siid": 18, "piid": 3, "access": ["read", "write"]},
        default=None,
    )
    timer: str = field(
        metadata={"siid": 18, "piid": 2, "access": ["read", "write"]},
        default=None,
    )
    fan_speed: int = field(
        metadata={"siid": 18, "piid": 6, "access": ["read", "write", "notify"], "enum": VacuumSpeed},
        default=None,
    )
    last_clean: int = field(
        metadata={"siid": 18, "piid": 13, "access": ["read", "notify"]},
        default=None,
    )
    total_clean_count: int = field(
        metadata={"siid": 18, "piid": 14, "access": ["read", "notify"]},
        default=None,
    )
    total_area: int = field(
        metadata={"siid": 18, "piid": 15, "access": ["read", "notify"]},
        default=None,
    )
    total_log_start: int = field(
        metadata={"siid": 18, "piid": 16, "access": ["read", "notify"]},
        default=None,
    )
    clean_success: int = field(
        metadata={"siid": 18, "piid": 18, "access": ["read", "notify"]},
        default=None,
    )
    water_level: int = field(
        metadata={"siid": 18, "piid": 20, "access": ["read", "write", "notify"], "enum": WaterLevel},
        default=None,
    )

    # siid 18 contd: water box
    water_box: int = field(
        metadata={"siid": 18, "piid": 9, "access": ["notify"]},
        default=None,
    )

    # siid 19: Consumable
    life_sieve: str = field(
        metadata={"siid": 19, "piid": 1, "access": ["read", "write"]},
        default=None,
    )
    life_brush_side: str = field(
        metadata={"siid": 19, "piid": 2, "access": ["read", "write"]},
        default=None,
    )
    life_brush_main: str = field(
        metadata={"siid": 19, "piid": 3, "access": ["read", "write"]},
        default=None,
    )

    # siid 20: Do Not Disturb
    dnd_enabled: bool = field(
        metadata={"siid": 20, "piid": 1, "access": ["read", "write"]},
        default=None,
    )
    dnd_start_time: str = field(
        metadata={"siid": 20, "piid": 2, "access": ["read", "write"]},
        default=None,
    )
    dnd_stop_time: str = field(
        metadata={"siid": 20, "piid": 3, "access": ["read", "write"]},
        default=None,
    )

    # siid 23: Map
    map_view: str = field(
        metadata={"siid": 23, "piid": 1, "access": ["read", "notify"]},
        default=None,
    )

    # siid 24: Audio
    audio_volume: int = field(
        metadata={"siid": 24, "piid": 1, "access": ["read", "write", "notify"]},
        default=None,
    )
    audio_language: str = field(
        metadata={"siid": 24, "piid": 3, "access": ["read", "write"]},
        default=None,
    )

    # siid 25: Timezone
    timezone: str = field(
        metadata={"siid": 25, "piid": 1, "access": ["read", "notify"]},
        default=None,
    )


class DreameVacuum(MiotDevice):
    """Dreame Vacuum MC1808 (Xiaomi Mi Robot Vacuum-Mop 1C) device."""

    _MAPPING = DreameStatus

    def status(self) -> DreameStatus:
        """Get device status."""
        return self.get_properties_for_dataclass(DreameStatus)

    def call_action(self, siid, aiid, params=None):
        """Call a MIoT action."""
        if params is None:
            params = []
        payload = {
            "did": f"call-{siid}-{aiid}",
            "siid": siid,
            "aiid": aiid,
            "in": params,
        }
        return self.send("action", payload)

    def set_fan_speed(self, speed: int):
        """Set fan speed (0=Silent, 1=Standard, 2=Strong, 3=Turbo)."""
        return self.set_property(fan_speed=speed)

    def return_home(self) -> None:
        """Start charging (siid 2, aiid 1)."""
        return self.call_action(2, 1)

    def start(self) -> None:
        """Start cleaning."""
        payload = [{"piid": 1, "value": 2}]
        return self.call_action(18, 1, payload)

    def stop(self) -> None:
        """Stop cleaning."""
        return self.call_action(18, 2)

    def find(self) -> None:
        """Locate the robot (siid 17, aiid 1)."""
        return self.call_action(17, 1)

    def reset_brush_life(self) -> None:
        """Reset main brush life (siid 26, aiid 1)."""
        return self.call_action(26, 1)

    def reset_filter_life(self) -> None:
        """Reset filter life (siid 27, aiid 1)."""
        return self.call_action(27, 1)

    def reset_side_brush_life(self) -> None:
        """Reset side brush life (siid 28, aiid 1)."""
        return self.call_action(28, 1)

    def zone_cleanup(self, coords: str) -> None:
        """Start zone cleaning with given coordinates."""
        payload = [{"piid": 1, "value": 19}, {"piid": 21, "value": coords}]
        return self.call_action(18, 1, payload)

    def set_water_level(self, water: int):
        """Set water level (1=Low, 2=Medium, 3=High)."""
        return self.set_property(water_level=water)

    def set_volume(self, volume: int):
        """Set audio volume (0-100)."""
        return self.set_property(audio_volume=volume)

    def set_dnd(self, enabled: bool, start_time: str = None, stop_time: str = None):
        """Set Do Not Disturb mode.

        Args:
            enabled: Enable or disable DND.
            start_time: Start time string (e.g. "22:00").
            stop_time: Stop time string (e.g. "07:00").
        """
        kwargs = {"dnd_enabled": enabled}
        if start_time is not None:
            kwargs["dnd_start_time"] = start_time
        if stop_time is not None:
            kwargs["dnd_stop_time"] = stop_time
        return self.set_property(**kwargs)

    def play_sound(self):
        """Play a sound/voice prompt (siid 24, aiid 3)."""
        return self.call_action(24, 3)

    def set_voice(self):
        """Set/download voice pack (siid 24, aiid 2)."""
        return self.call_action(24, 2)

    def remote_start(self, velocity: int, rotation: int):
        """Start remote control movement.

        siid 21 (remote), aiid 1 (start-remote)
        piid 1 = deg (rotation in degrees, string)
        piid 2 = speed (velocity, string)
        """
        payload = [
            {"piid": 1, "value": str(rotation)},
            {"piid": 2, "value": str(velocity)},
        ]
        return self.call_action(21, 1, payload)

    def remote_stop(self):
        """Stop remote control movement (siid 21, aiid 2)."""
        return self.call_action(21, 2)

    def remote_exit(self):
        """Exit remote control mode (siid 21, aiid 3)."""
        return self.call_action(21, 3)
