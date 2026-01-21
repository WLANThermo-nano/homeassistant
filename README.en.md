# WLANThermo  – Home Assistant Custom Integration

![Version](https://img.shields.io/badge/version-0.2.1-informational)
![License](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025%2B-blue)
[![Support](https://img.shields.io/badge/support-WLANThermo%20Forum-lightgrey)](https://wlanthermo.de/forums/)
![Owner](https://img.shields.io/badge/code%20owner-@MStapelfeldt-purple)

---

## Notice & Disclaimer

This is a **community integration** for WLANThermo devices.  
There is **no official support** by the author or the WLANThermo team.

- Forks, further development, and bugfixes are welcome  
- For questions & discussions, please use the  
  👉 **[WLANThermo Forum](https://wlanthermo.de/forums/)**

⚠️ **No warranty / Use at your own risk**

---

## Overview

This integration connects Home Assistant to **WLANThermo devices**  
(ESP32 / Nano / Mini / Link).

It reads sensor data, system status, and pitmaster information and exposes them as native Home Assistant entities.

The integration is **fully UI-based**, no YAML required.

---

## Features

- 🔍 Automatic discovery & setup via the HA UI
- 🌡️ Dynamic temperature sensors for all channels (name & number)
- 🎛️ Dynamic pitmaster sensors (power, temperature, mode, PID, channel)
- ⏱️ **Time Left sensor** for each active channel
- ☁️ **Cloud sensors**
- 🔋 System diagnostics:
  - WiFi RSSI
  - Battery level
  - Charging state
- 🎨 Channel colors as **light entities**
- 🌍 Full **translation support (EN / DE)**
- ⚙️ Configurable scan interval
- 🔌 Offline-tolerant startup (entities appear automatically)
- 🔄 Options flow for advanced settings
- 👻 Option: Show inactive sensors as *unavailable*

---

## Dashboard (optional)

For the included sample dashboard `wlanthermo_en.yaml`, the following frontend extensions are required (via **HACS → Frontend**):

- Auto-Entities
- Button Card
- Mushroom
- ApexCharts Card
- Card Mod

**Important:**  
Replace all occurrences of `wlanthermo` with your device name.
All entity names are in English. For German, use the German dashboard file.

Example:
```yaml
device_name: wlanthermo → nano_v3
sensor.wlanthermo_channel_*_temperature → sensor.nano_v3_channel_*_temperature
```

## Installation via HACS (recommended)

1. Open Home Assistant and go to  
   **Settings → Devices & Services → HACS**
2. Select **Integrations**
3. Click the three dots (⋮) in the top right → **Custom Repository**
4. Enter: `https://github.com/WLANThermo-nano/homeassistant` Type: **Integration**
5. Search for **WLANThermo**
6. Install the integration
7. Restart Home Assistant

---

## Manual Installation

1. Download or extract the repository
2. Copy the folder `custom_components/wlanthermo` to `<HA config>/custom_components/`
3. Restart Home Assistant

---

## Setup

1. Open Home Assistant
2. **Settings → Devices & Services → Add Integration**
3. Select **WLANThermo**
4. Enter IP address / host, port, and optional path prefix
5. Complete the setup

---

## Integration Options

Access options via:

**Settings → Devices & Services → WLANThermo → Options**

### Available Options

- **IP address / host**
- Can be updated if the internal IP changes in your router

- **Scan interval**
- Defines how often data is fetched from the WLANThermo
- Default: **10 seconds**

- **Inactive sensor display**
- Show `999` or as **unavailable**

- **Authentication**
- Username / password if enabled in the web interface

---

## Entities (Selection)

### Channels
- Temperature
- Alarm mode (Select)
- Sensor type (Select)
- Min / Max
- **Time Left**
- Color (Light / Text)

### Pitmaster
- Power (%)
- Temperature
- Mode (Auto / Manual / Off)
- PID profile
- Assigned channel

### System / Diagnostics
- WiFi RSSI
- Battery level
- Charging state
- Cloud status
- Cloud URL
- Device & system information

---

## Sensor: Time Left

For each temperature channel, a  
`channel_*_timeleft` sensor is automatically created.

### Calculation

- Based on the average temperature change
- Sliding time window (several minutes)

Formula:
```
Time left (min) =
(Target temperature – current temperature) / temperature increase per minute
```

### Behavior

- Decreasing or stagnating temperature → **0 minutes**
- Disconnected channels → **no value**

Ideal for grilling & cooking processes 🔥

---

## API Notes

- Official HTTP API:  
  https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP

- Use routes in **lowercase**:
```
/setpitmaster
/setchannels
/setpid
/setsystem
```

---

## Development & Contributions

Pull requests, bug reports, and feature requests are welcome ❤️  
Please include logs and a clear error description if possible.
