# Xiaomi Mi Robot Vacuum-Mop 1C

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom Home Assistant integration for the **Xiaomi Mi Robot Vacuum-Mop 1C** (Dreame MC1808, model `dreame.vacuum.mc1808`).

Communicates locally via the MIoT protocol over UDP (port 54321) — no cloud dependency.

## Features

- Full vacuum control: start, stop, pause, return to dock, locate
- Fan speed modes: Silent, Standard, Medium, Turbo
- Water level control: Low, Medium, High
- Zone cleaning
- Remote control (forward, backward, rotate left/right)
- Do Not Disturb mode (enable/disable, set quiet hours)
- Water box (mop pad) detection
- Audio controls (play sound, set voice pack, volume)
- Diagnostic sensors:
  - Main brush life remaining (% and hours)
  - Side brush life remaining (% and hours)
  - Filter life remaining (% and hours)
  - Total cleaning count and area
  - Current cleaning time and area
  - Last error

## Requirements

- Device token (obtain via [miio2.db extraction](https://python-miio.readthedocs.io/en/latest/discovery.html#extracting-tokens) or similar method)
- Device must be on the same local network as Home Assistant

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner, select **Custom repositories**
3. Add `https://github.com/Tipasha/xiaomi_vacuum_1c` with category **Integration**
4. Click **Download** on the integration card
5. Restart Home Assistant
6. Go to **Settings → Devices & Services → Add Integration**
7. Search for **Xiaomi Mi Robot Vacuum-Mop 1C**
8. Enter the device IP address and token

### Manual

1. Copy the `xiaomi_vacuum_1c` folder to `/config/custom_components/` on your Home Assistant instance
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration**
4. Search for **Xiaomi Mi Robot Vacuum-Mop 1C**
5. Enter the device IP address and token

## Services

### `xiaomi_vacuum_1c.remote_control_move`

Move the vacuum using remote control.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `velocity` | int | yes | Speed, -300 to 300. Positive = forward, negative = backward. |
| `rotation` | int | yes | Rotation, -120 to 120. Positive = left, negative = right. |

### `xiaomi_vacuum_1c.remote_control_stop`

Stop the current remote control movement.

### `xiaomi_vacuum_1c.remote_control_exit`

Exit remote control mode.

### `xiaomi_vacuum_1c.set_dnd`

Set Do Not Disturb mode.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `enabled` | bool | yes | Enable or disable DND. |
| `start_time` | string | no | Start time (e.g. `"22:00"`). |
| `stop_time` | string | no | Stop time (e.g. `"07:00"`). |

### `xiaomi_vacuum_1c.play_sound`

Play a voice prompt on the vacuum.

### `xiaomi_vacuum_1c.set_voice`

Download and apply the configured voice pack.

### `vacuum.send_command`

All features above are also available via the standard `vacuum.send_command` service:

| Command | Parameters |
|---|---|
| `set_water_level` | `{"water_level": "Low"}` or `{"water_level": 1}` |
| `remote_control_move` | `{"velocity": 200, "rotation": 0}` |
| `remote_control_stop` | — |
| `remote_control_exit` | — |
| `set_dnd` | `{"enabled": true, "start_time": "22:00", "stop_time": "07:00"}` |
| `play_sound` | — |
| `set_voice` | — |

## Remote Control Card Example

```yaml
type: grid
columns: 3
cards:
  - type: button
    name: ""
    tap_action:
      action: none
  - type: button
    name: Forward
    icon: mdi:arrow-up-bold
    tap_action:
      action: perform-action
      perform_action: xiaomi_vacuum_1c.remote_control_move
      data:
        velocity: 200
        rotation: 0
  - type: button
    name: ""
    tap_action:
      action: none
  - type: button
    name: Left
    icon: mdi:arrow-left-bold
    tap_action:
      action: perform-action
      perform_action: xiaomi_vacuum_1c.remote_control_move
      data:
        velocity: 0
        rotation: 60
  - type: button
    name: Stop
    icon: mdi:stop
    tap_action:
      action: perform-action
      perform_action: xiaomi_vacuum_1c.remote_control_stop
  - type: button
    name: Right
    icon: mdi:arrow-right-bold
    tap_action:
      action: perform-action
      perform_action: xiaomi_vacuum_1c.remote_control_move
      data:
        velocity: 0
        rotation: -60
```
