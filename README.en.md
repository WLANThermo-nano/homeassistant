# WLANThermo – Home Assistant Integration

![Version](https://img.shields.io/badge/version-0.3.0-informational)
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

This integration connects Home Assistant to **WLANThermo devices**.

It reads sensor data, system status, and pitmaster information and exposes them as native Home Assistant entities.

The integration is **fully UI-based**, no YAML required.

### Compatibility

This integration has been successfully tested with:

- WLANThermo Nano V1+, V3
- WLANThermo Mini V2 ESP32, V3
- WLANThermo Link V1
- Home Assistant 2026.1.0 and newer

Other models and firmware versions may also work, but are not officially tested.

---

## Features

- 🔍 Automatic discovery & setup via the HA UI
- 🌡️ Dynamic temperature sensors for all channels (name & number)
- 🎛️ Dynamic pitmaster sensors (power, temperature, mode, PID, channel)
- ⏱️ Time Left sensor for each active channel
- ✉️ Configuration of notifications via Pushover and Telegram
- 📶 Bluetooth temperature sensor configuration
- ☁️ Cloud sensors
- 🔋 System diagnostics:
  - WiFi RSSI
  - Battery level
  - Charging state
- 🎨 Channel colors
- 🌍 Full translation support (EN / DE)
- ⚙️ Configurable scan interval
- 🔌 Offline-tolerant startup (entities appear automatically)
- 🔄 Options flow for advanced settings
- 👻 Option: Show inactive sensors as *unavailable*

---

## Dashboard (optional)

For the sample dashboard `wlanthermo_en.yaml` within the Repository, the following frontend extensions are required (via **HACS → Frontend**):

- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) (`auto-entities`)
- [Button Card](https://github.com/custom-cards/button-card) (`button-card`)
- [Mushroom](https://github.com/piitaya/lovelace-mushroom) (`Mushroom`)
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) (`apexcharts-card`)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) (`card-mod`)
- [Browser Mod](https://github.com/thomasloven/hass-browser_mod) (`browser-mod`)

**Important:**  
Replace all occurrences of `wlanthermo` with your device name.
All entity names are in English by default. For German, use the `wlanthermo.yaml` dashboard file and entity names.

Example:
```yaml
device_name: wlanthermo → nano_v3
sensor.wlanthermo_channel_*_temperature → sensor.nano_v3_channel_*_temperature
sensor.nano_v3_channel_*_temperature → sensor.wlanthermo_kanal_*_temperature
```

---

## Installation via HACS (recommended)

1. Open Home Assistant and go to  
   **Menu → HACS** (your_HA_URL/hacs/dashboard)
2. Click the three dots (⋮) in the top right → **Custom Repository**
3. Enter: `https://github.com/WLANThermo-nano/homeassistant` Type: **Integration**
4. Search for **WLANThermo**
5. Install the integration
6. Restart Home Assistant

## Manual Installation

1. Download or extract the repository
2. Copy the folder `custom_components/wlanthermo` to `<HA config>/custom_components/`
3. Restart Home Assistant

---

## Setup

1. Open Home Assistant
2. **Settings → Devices & Services → Add Integration**
3. Select **WLANThermo**
4. Enter device name (should be unique)
5. Enter IP address / host, port, and optional path prefix
6. The option 'Show inactive sensors as unavailable' controls whether temperatures are shown as `999` or as **unavailable**
7. If authentication is required, enable it and enter username/password
8. Complete the setup

---

## Integration Options

Access options via:

**Settings → Devices & Services → WLANThermo → Options (gear icon)**

- **IP address / port / prefix**  
  Can be updated if the IP changes in your router or settings change
- **Scan interval**  
  Defines how often data is fetched from the WLANThermo  
  Default: **10 seconds**
- **Show inactive sensors as unavailable**  
  Controls whether temperatures are shown as `999` or as **unavailable**
- **Authentication**  
  Username / password if enabled in the web interface

---

## Entities in HA

### Channels
- Sensors
  - Temperature
  - [Time Left](#sensor-time-left)
- Controls
  - Alarm mode
  - Sensor type
  - Min / Max
- Configuration
  - Name
  - Color

### Pitmaster
- Sensors
  - Power (%)
  - Temperature
- Controls
  - Assigned channel
  - Mode (Auto / Manual / Off)
  - PID profile
  - Set temperature

### PID Profile
- Configuration
  - Name
  - Actuator
  - Min / Max PWM (SSR / FAN / DAMPER)
  - Min / Max Servo Pulse (SERVO / DAMPER)
  - Start power
  - Actuator linking (DAMPER)
  - Lid detection

### System
- Diagnostics
  - WiFi RSSI
  - Battery level
  - Charging state
  - Cloud status
  - Cloud URL
  - Device & system information
  - Restart Integration

### Notification
- Configuration
  - Activate notification (Telegram/Pushover)
  - Enter Token (Telegram/Pushover)
  - User Key / Chat ID (Telegram/Pushover)
  - Set Message priority (Pushover)
  - Send test message (Telegram/Pushover)

### Bluetooth
- Configuration
  - Activate Bluetooth
  - Selection of available Channels

**Important** you need to restart the integration after changing Bluetooth Settings to discover BT Sensors.  
Use the "Reload Integration" button from System Diagnostics.

---

## Sensor: Time Left

For each temperature channel, a  
`channel_*_timeleft` sensor is automatically created.

Calculation:
- Based on the average temperature change
- Sliding time window (several minutes)

Formula:
```
Time left (min) =
(Target temperature – current temperature) / temperature increase per minute
```

Behavior
- Decreasing or stagnating temperature → **0 minutes**
- Disconnected channels → **no value**

Ideal for grilling & cooking processes 🔥

## Notification Configuration

To set up Telegram or Pushover, you need a token and a Chat ID/User key. Instructions for setting these up can be found at [Push-Notification](https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/Push-Notification).
You can only test the notification if both text fields are filled in.

---

## API Notes

- Official HTTP API: (Nano V1(+) are almost the same)  
  https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP

---

## Development & Contributions

Pull requests, bug reports, and feature requests are welcome ❤️  
Please include logs and a clear error description if possible.
