# WLANThermo BBQ – Home Assistant Custom Integration

![Version](https://img.shields.io/badge/version-0.0.1-informational)
![License](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024%2B-blue)
![Support](https://img.shields.io/badge/support-No%20support%20provided-lightgrey)
![Owner](https://img.shields.io/badge/code%20owner-@MStapelfeldt-purple)

**Version:** 0.1.0  
**Code Owner:** @MStapelfeldt  
**License:** MIT

> **Attribution & Disclaimer**
> This is a community integration for WLANThermo BBQ.  
> **No support** is provided by the author. Forks, contributions, and bugfixes are welcome.  
> **No warranty/liability** — use at your own risk.

## Overview
This integration connects Home Assistant to a WLANThermo BBQ (ESP32/Nano/Next). It reads sensor and pitmaster data and exposes them as entities.

## Features
 - Pitmaster channel select: choose and view the selected channel for each pitmaster
 - Dynamic cloud status sensor: always reflects the latest connection state
 - Improved translation support for all status and select values

## API Reference
- Official HTTP API: https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP
- Use lowercase routes (`/setpitmaster`, `/setchannels`, `/setpid`, `/setsystem`)
- For pitmaster writes: send complete nested PM objects in an array

## Manual Installation
1. Extract this repository
2. Copy `custom_components/wlanthermo_bbq` into `<HA config>/custom_components/`
3. Restart Home Assistant

## Installation via HACS

1. Open Home Assistant and go to **Settings → Devices & Services → HACS**.
2. Select **Integrations** and click the three dots (⋮) in the top right → **Custom repositories**.
3. Enter this repository URL: `https://github.com/MStapelfeldt/wlanthermo_bbq` and select **Integration** as type.
4. Search for **WLANThermo BBQ** in HACS, install the integration, and restart Home Assistant.

## Setup
1. Open Home Assistant
2. Go to Settings → Devices & Services → **Add Integration** → **WLANThermo BBQ**
3. Enter host, port, and (if needed) path prefix

## Integration Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **WLANThermo BBQ** and select it.
3. Enter the IP address of your WLANThermo BBQ device and select the model if needed.
4. Complete the setup and select the desired version if multiple are shown.

## Entities (Examples)
- **Pitmaster**: duty cycle, channel, PID status, setpoint
- **Channels**: temperature, alarm, sensor type, min/max, Time Left
- **System**: RSSI, battery status, charging

### New Sensor: Time Left

For each temperature channel, a `channel_time_left` sensor is automatically created. This sensor shows the estimated remaining time (in minutes) until the current temperature reaches the configured target (Max).

**Calculation:**
- The time left is based on the average temperature change over the last few minutes (sliding window).
- The formula is:

	Time Left (min) = (Target Temperature - Current Temperature) / (Temperature Rise per Minute)

- If the temperature is stagnant or falling, the sensor will show 0.
- If the channel is not connected or no data is available, the sensor will be empty.

**Use Case:**
- Useful for grilling or cooking to estimate when your food will be ready.

## Configuration
The integration uses a configuration dialog (config flow). No manual YAML entries are required.

## Development & Contributions
Pull requests, bug reports, and feature requests are welcome!
