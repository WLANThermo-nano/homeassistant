
# WLANThermo – Home Assistant Integration

![Version](https://img.shields.io/badge/version-0.2.3-informational)
![License](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/HA-2025.12%2B-blue)
[![Support](https://img.shields.io/badge/support-WLANThermo%20Forum-lightgrey)](https://wlanthermo.de/forums/)
![Maintainer](https://img.shields.io/badge/maintainer-@MStapelfeldt-informational)
![Owner](https://img.shields.io/badge/code%20owner-@sochs-purple)

---

## Notice & Disclaimer

This is a **community integration** for WLANThermo devices.  
There is **no official support** by the author or the WLANThermo team.

- Forks, further development, and bugfixes are welcome  
- For questions & discussions, please use the  
  👉 **[WLANThermo Forum](https://wlanthermo.de/forums/)**

⚠️ **No warranty / Use at your own risk**

---

## Documentation & Wiki

For detailed information, see the [German Wiki](docs/de/README.md) or [English Wiki](docs/en/README.md).

---

## Quick Overview

This integration connects Home Assistant with **WLANThermo devices** and provides sensor data, system status, and pitmaster information as native Home Assistant entities.

The integration is **fully UI-based**, YAML is not required.

### Compatibility

This integration has been tested with:

- WLANThermo Nano V1+, V3
- WLANThermo Mini V2 ESP32, V3
- WLANThermo Link V1
- Home Assistant 2026.1.0 and newer

Other models and firmware versions may also work but are not tested.

---

## Features

- 🔍 Automatic detection & setup via the HA UI
- 🌡️ Dynamic temperature sensors for all channels (name & number)
- 🎛️ Dynamic pitmaster sensors (power, temperature, mode, PID, channel)
- ⏱️ Remaining time sensor per active channel
- ✉️ Notification configuration via Pushover and Telegram
- 📶 Bluetooth temperature sensor configuration
- ☁️ Cloud sensors
- 🔋 System diagnostics:
  - WiFi RSSI
  - Battery level
  - Charging state
- 🎨 Channel colors
- 🌍 Full translation support (DE / EN)
- ⚙️ Configurable scan interval
- 👻 Option: Show inactive sensors as *unavailable*

---


## Dashboard (optional)

The sample dashboard `wlanthermo_en.yaml` is optional and serves as a template.  

[Dashboard explanation](docs/en/dashboard.md)

---

## Installation

[Installation](docs/en/setup.md)
via HACS (recommended):  
**Custom Repository**: `https://github.com/WLANThermo-nano/homeassistant`  
manual:  
Copy `custom_components/wlanthermo` to `<HA config>/custom_components/`

---

## Setup

[Setup](docs/en/setup.md#setup)
1. **Settings → Devices & Services → Add Integration**
2. Select **WLANThermo**
3. Enter IP address / host
4. Click OK

---

## Integration Options

You can access the options via:

**Settings → Devices & Services → WLANThermo → Options/gear icon**
[Options](docs/en/setup.md#integration-options)

---

## Entities in HA

👉 For all entity details, see the Wiki:  
[Entities & Sensors](docs/en/entities.md)

## Development

[Development](docs/en/development.md)

## WIKI
- [FAQ](docs/en/faq.md)
- [Troubleshooting](docs/en/troubleshooting.md)
- [API Notes](docs/en/api.md)

---
[🇩🇪 Deutsch](../de/README.md) | [🇬🇧 English](../en/README.md)