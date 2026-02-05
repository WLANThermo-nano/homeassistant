# Setup & Installation

## Installation via HACS (recommended)

1. Open Home Assistant and go to  
   **Menu → HACS** (your_HA_URL/hacs/dashboard)
2. Click the three dots (⋮) in the top right → **Custom Repository**
3. Enter the following URL: `https://github.com/WLANThermo-nano/homeassistant` Type: **Integration**
4. Then search for **WLANThermo**  
   If HACS does not show the repository immediately, refresh your browser.
5. Install the integration
6. Restart Home Assistant

## Manual Installation

1. Download or extract the repository
2. Copy the folder `custom_components/wlanthermo` to `<HA config>/custom_components/`
3. Restart Home Assistant

## Setup
1. **Settings → Devices & Services → Add Integration**
2. Search and select **WLANThermo**
3. In the dialog, configure your WLANThermo:
   - First, enter a device name or leave it as WLANThermo.  
     Important: If you have 2 or more devices, choose unique names to easily identify the correct sensors for each device.  
     Sensor names are always composed as device_name_channel_*_* (or similar).
   - Host/IP is the address you use in your browser to access the web interface. For example, 192.168.178.101 (no http:// needed).
   - The default port is 80, so you can usually leave this as is.
   - If you have not changed the API configuration, the prefix / is correct → do not change.
   - By default, WLANThermo sends not connected channels with temperature 999°C. The integration detects this and sets them to "Unavailable" automatically.  
     If you disable this option, sensors with temperature 999.0 will be shown in the frontend.
   - Some devices require authentication to change settings.  
     If unsure, open an incognito browser window, try to edit settings in WLANThermo, and see if you are prompted for username and password. If so, enter these in the fields and enable "Authentication required".
4. Complete the setup by clicking OK
5. You will then see an integration entry with a device, version number, and over 100 sensors.

## Integration Options

You can access the options via:

**Settings → Devices & Services → WLANThermo → Options/gear icon**

- The device name CANNOT be changed. To change it, delete and re-add the device.
- **IP address / Port / Prefix**  
  Can be adjusted if the IP changes in your router or settings have changed
- **Scan interval**  
  Defines how often data is polled from WLANThermo  
  By default, the integration polls every **10 seconds** for new values. If you want more frequent updates, you can set this under scan interval.  
  Please note: very short intervals (1 second) require a lot of processing power and may slow down your network and Home Assistant.
- **Show inactive sensors as unavailable**  
  Controls whether temperatures of `999` are shown or marked as **unavailable**
- **Authentication**  
  Username / password, if enabled in the web interface

---
[🇩🇪 Deutsch](../de/README.md) | [🇬🇧 English](../en/README.md)
