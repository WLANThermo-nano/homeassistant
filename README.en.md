# WLANThermo  – Home Assistant Custom Integration

![Version](https://img.shields.io/badge/version-0.1.4-informational)
![License](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025%2B-blue)
[![Support](https://img.shields.io/badge/support-WLANThermo%20Forums-lightgrey)](https://wlanthermo.de/forums/)
![Owner](https://img.shields.io/badge/code%20owner-@MStapelfeldt-purple)

> **Attribution & Disclaimer**
> This is a community integration for WLANThermo.  
> **No support** is provided by the author. Forks, contributions, and bugfixes are welcome. For any questions, use the [WLANThermo Forum](https://wlanthermo.de/forums/)
   
> **No warranty/liability** — use at your own risk.


## Dashboard Requirements
To use the included dashboard (wlanthermo.yaml), please install the following frontend cards/extensions from HACS:

- Auto-Entities
- Button Card
- Mushroom
- ApexCharts Card
- Card Mod

Install these via HACS → Frontend before importing or using the dashboard.
The dashboard is designed to be as dynamic as possible. However, you must replace all occurrences of `wlanthermo` with your actual device name.
For example: `device_name: wlanthermo` → `device_name: nano_v3` or `entity_id: sensor.wlanthermo_channel_*_temperatur` → `entity_id: sensor.nano_v3_channel_*_temperatur`

## Overview
This integration connects Home Assistant to a WLANThermo (ESP32/Nano/Link/Mini). It reads sensor and pitmaster data and exposes them as entities.

## Features
- Automatic discovery and setup via the Home Assistant interface
- Temperature sensors for all channels (name & number)
- Pitmaster sensors (e.g., duty cycle)
- System information: RSSI, battery status, charging state
- Configurable scan intervals
- Support for various WLANThermo models
- Offline-tolerant startup (entities become available once the device is online)
- Pitmaster channel selection: display and choose a channel for each pitmaster
- Dynamic cloud status sensor: always shows the current connection status
- Improved translation support for all status and selection values
- New light sensor for color picking
- Configuration flow and options flow for advanced settings
- Switch to display sensor temperature as 999 or unavailable

## API Reference
- Official HTTP API: https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP
- Use routes in **lowercase** (`/setpitmaster`, `/setchannels`, `/setpid`, `/setsystem`)
- For pitmaster writes: send complete nested PM objects in the array

## Manual Installation
1. Extract the repository
2. Copy `custom_components/wlanthermo` to `<HA config>/custom_components/`
3. Restart Home Assistant

## Installation via HACS

1. Open Home Assistant and go to **Settings → Devices & Services → HACS**.
2. Select **Integrations** and click the three dots (⋮) in the top right → **Custom Repository**.
3. Enter the URL of this repository: `https://github.com/WLANThermo-nano/homeassistant` and select **Integration** as the type.
4. Search for **WLANThermo** in HACS, install the integration, and restart Home Assistant.

## Setup
1. Open Home Assistant
2. Go to Settings → Devices & Services → **Add Integration** → **WLANThermo**
3. Provide the host, port, and optional path prefix

### Integration Options

The integration provides an options flow that allows users to adjust the following settings:

1. **IP Address:**
   - Can be updated if the internal IP changes in the router.

2. **Scan Interval:**
   - Define how often the integration fetches data from the WLANThermo device.
   - Default value: 10 seconds.

3. **Sensor Temperature Display:**
   - Choose whether the sensor temperature is displayed as `999` or `unavailable` when no data is present.

4. **Authentication:**
   - Adjust and set authentication if required in the web interface.

These options can be changed at any time via the Home Assistant interface:

1. Go to **Settings → Devices & Services → Edit Integration**.
2. Select the desired integration entry.
3. Adjust the options in the displayed dialog.

## Entities (Examples)
- **Pitmaster**: Duty cycle, channel, PID status, setpoint
- **Channels**: Temperature, alarm, sensor type, min/max, remaining time (time left)
- **System**: RSSI, battery status, charging state
- **Light Sensor**: Color temperature, brightness

### Sensor: Remaining Time (Time Left)

For each temperature channel, a `channel_*_time_left` sensor is automatically created. This shows the estimated remaining time (in minutes) until the current temperature reaches the set target (max).

**Calculation:**
- The remaining time is based on the average temperature change over the last few minutes (sliding window).
- The formula is:

	Remaining time (min) = (Target temperature - Current temperature) / (Temperature increase per minute)

- If the temperature stagnates or decreases, 0 is displayed.
- If the channel is not connected or no data is available, the sensor remains empty.

**Use Case:**
- Useful for grilling or cooking processes to estimate when the food will be ready.

### Sensor: Channel Color (Switch)

For each channel, a `light.wlanthermo_channel_*_color` sensor is automatically created. This is technically a light entity but is used here as a color picker for the channel color.

**Note:**
- The sensor can only be used for connected channels/sensors.
- The value is the same as the text field.
- Turning off, brightness, and the switch have no function.

## Configuration
The integration uses a configuration dialog (config flow). No manual YAML entries are required.

## Development & Contributions
Pull requests, bug reports, and feature requests are welcome!
