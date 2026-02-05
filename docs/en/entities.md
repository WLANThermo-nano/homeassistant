# Entities & Sensors

This page describes the entities and sensors provided by the integration.

### Channels
- Sensors
  - Temperature
  - Remaining time
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
  - Target temperature

### Pit Profile
- Configuration
  - Name
  - Actuator
  - Min / Max PWM (SSR / FAN / DAMPER)
  - Min / Max servo pulse (SERVO / DAMPER)
  - Start power
  - Actuator link (DAMPER)
  - Lid detection

### System
- Diagnostics
  - WiFi RSSI
  - Battery level
  - Charging state
  - Cloud status
  - Cloud URL
  - and others  
    Device & system information

### Notifications
- Configuration
  - Enable notifications (Telegram/Pushover)
  - Enter token (Telegram/Pushover)
  - User key / Chat ID (Telegram/Pushover)
  - Set message priority (Pushover)
  - Send test message (Telegram/Pushover)

### Bluetooth
- Configuration
  - Enable Bluetooth
  - Select channels to transmit  

**Important:** After changing Bluetooth settings, you must restart the integration so BT sensors are detected.  
Use the "Restart integration" button in system diagnostics.

## Entities
All entities are divided into 4 categories:  
- Controls  
- Sensors  
- Configuration  
- Diagnostics  

### Controls
Used to adjust common settings.
- Alarm mode – All channels with temperature sensor plugged in/connected or 999°C  
  Here you can choose whether to be notified by buzzer, push, or both.  
  For push, notifications must be enabled and configured first.
- Maximum / Minimum – All channels with temperature sensor plugged in/connected or 999°C  
- Sensor type – All channels with temperature sensor that are not "fixed" (no Bluetooth and K-type)  
- Pitmaster channel – Mapping from pitmaster to temperature, only possible for plugged-in sensors (no Bluetooth)
  If a channel appears as "   " or "unknown", please re-enter the channel name, see [Configuration](#configuration)
- Pitmaster power – Only when mode is set to manual  
- Pitmaster mode – Auto (regulation by temperature), Manual (regulation by power), or Off  
- Pitmaster temperature – Only when mode is set to auto  

### Sensors
Can only be read, not set.
- Channel temperature – Shows temperature if plugged in or 999°C. If "Show inactive sensors as unavailable" is enabled,  
  each temperature has the channel number hidden in the attributes.
- Channel remaining time – Calculated from active sensors as long as temperature is rising  
- Pitmaster power – In auto mode, shows how fast the fan is spinning (percent), otherwise not available  
- Pitmaster temperature – Mirrors the temperature of the current channel.  
  If pit channel is set to 1, pit temperature = channel 1 temperature
Important to know:  
If Bluetooth sensors are connected, they must be initialized once. To do this, activate the Bluetooth channels and restart the integration.

### Configuration
All settings that do not need to be changed/adjusted frequently.  
- Channel color – Can be used in the web interface and for graphs to distinguish temperatures.  
  This uses a "workaround" via a light entity. The advantage is that you can easily set and select a color, but there are settings like brightness and on/off that are not considered.
- Channel name – Can be changed to name channels. Sometimes names may appear as Unknown or "   ", which means they are not defined in the device itself. Just rename them once.
- Bluetooth settings can be toggled on and off via switches. Note that the integration may need to be restarted several times. Best practice:  
  Enable Bluetooth → restart integration  
  Enable Bluetooth *** (this is the name of the BT device, e.g. Meater, cannot be changed, plus last 6 digits of MAC address) probe 1 - X  
  (after switching, wait 5 seconds, as the setting is only sent then) → restart integration  
  Now the probes are available under channel X  
- PID profile settings – Here you can make detailed settings for the pit profiles (but not everything).  
  Name – Simple, just give it a name so you know what you are setting.  
  Each profile can be linked to an "actuator", which also affects the settings:  
  - SSR – Solid State Relay or DC relay/transistor  
  - FAN – Fan  
  - SERVO – Motor controlled by PWM  
  - DAMPER – Vent control  
   PWM minimum/maximum is only for SSR, Fan, and Damper  
   Servo minimum/maximum is only for Servo and Damper  
   Start power can determine the maximum power to start the grill. This is useful to avoid overshooting/overheating by starting at 100%.  
   Actuator link can be used with Damper to link between actuators  
   Lid detection indicates whether rapid temperature drops are detected as "lid open" and the fan is briefly paused instead of compensating  
- Push settings – Reflect the web settings for notifications. See the [WlanThermo Wiki](https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/Push-Notification).  
  Testing only works if token and ChatID/UserKey are set

---

## Remaining Time Sensor

For each temperature channel, a sensor  
`channel_*_remaining_time` is automatically created.

Calculation:
- Based on the average temperature change
- Sliding time window (several minutes)

Formula:
```
Remaining time (min) =
(Target temperature – current temperature) / temperature increase per minute
```

Behavior
- Falling or stagnant temperature → **0 minutes**
- Not connected channels → **no value**
- The calculation is intentionally smoothed to avoid jumps.

Ideal for grilling & cooking processes 🔥
---
[🇩🇪 Deutsch](../de/README.md) | [🇬🇧 English](../en/README.md)
