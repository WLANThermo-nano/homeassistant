
"""
Sensor platform for WLANThermo
Exposes system, channel, pitmaster, and temperature sensors as Home Assistant entities.
Includes diagnostic and device info sensors.
"""

from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from homeassistant.core import callback
from .const import DOMAIN
from datetime import timedelta
from .data import WlanthermoData
import logging
import collections

_LOGGER = logging.getLogger(__name__)


class WlanthermoChannelTemperatureSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for a channel's temperature.
    Reports the current temperature for each channel.
    """
    def __init__(self, coordinator, channel, field=None):
        super().__init__(coordinator)
        self._channel_number = channel.number
        # Try to get a friendly device name from the coordinator or fallback
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo_BBQ")
            else:
                device_name = "WLANThermo_BBQ"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_has_entity_name = True
        self._attr_translation_key = "channel_temperature"
        self._attr_translation_placeholders = {"channel_number": str(self._channel_number)}
        self._attr_unique_id = f"{safe_device_name}_channel_{self._channel_number}_temperatur"
        self.entity_id = f"sensor.{safe_device_name}_channel_{self._channel_number}_temperatur"
        self._attr_icon = "mdi:thermometer"

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        channels = getattr(self.coordinator.data, 'channels', [])
        for ch in channels:
            if ch.number == self._channel_number:
                return ch
        return None


    @property
    def device_info(self):
        """
        Return device info for Home Assistant device registry.
        """
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            device_info = hass.data[DOMAIN][entry_id]["device_info"].copy()
            api = hass.data[DOMAIN][entry_id].get("api")
            settings = getattr(api, "settings", None)
            if settings and hasattr(settings, "device"):
                dev = settings.device
                device_info["sw_version"] = getattr(dev, "sw_version", None)
                device_info["hw_version"] = getattr(dev, "hw_version", None)
                device_info["model"] = f"{getattr(dev, 'device', None)} {getattr(dev, 'hw_version', None)} {getattr(dev, 'cpu', None)}"
            return device_info
        return None


    @property
    def state(self):
        """
        Return the current temperature value, or None if sensor is not connected (999.0).
        """
        channel = self._get_channel()
        if not channel:
            return None
        temp = getattr(channel, 'temp', None)
        show_inactive = (
            self.coordinator.config_entry.options.get("show_inactive_unavailable",
                self.coordinator.config_entry.data.get("show_inactive_unavailable", True)
            )
        )
        if temp == 999.0 and show_inactive:
            return None
        return temp
        

    @property
    def available(self):
        """
        Return True if the channel is available and not marked as inactive.
        """
        channel = self._get_channel()
        if not channel:
            return False
        show_inactive = (
            self.coordinator.config_entry.options.get("show_inactive_unavailable",
                self.coordinator.config_entry.data.get("show_inactive_unavailable", True)
            )
        )
        temp = getattr(channel, "temp", None)
        if temp == 999.0 and show_inactive:
            return False
        return True


class WlanthermoChannelTimeLeftSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity estimating time left until the channel reaches its max temperature.
    Uses a moving window to estimate rate of temperature change.
    """
    def __init__(self, coordinator, channel, window_seconds=300):
        super().__init__(coordinator)
        self._channel_number = channel.number
        # Try to get a friendly device name from the coordinator or fallback
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo_BBQ")
            else:
                device_name = "WLANThermo_BBQ"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_has_entity_name = True
        self._attr_translation_key = "channel_time_left"
        self._attr_translation_placeholders = {"channel_number": str(self._channel_number)}
        self._attr_unique_id = f"{safe_device_name}_channel_{self._channel_number}_timeleft"
        self.entity_id = f"sensor.{safe_device_name}_channel_{self._channel_number}_timeleft"
        self._attr_icon = "mdi:timer"
        self._attr_native_unit_of_measurement = "min"
        self._window_seconds = window_seconds
        self._history = collections.deque(maxlen=60)  # store (timestamp, temp)

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        channels = getattr(self.coordinator.data, 'channels', [])
        for ch in channels:
            if ch.number == self._channel_number:
                return ch
        return None

    @property
    def device_info(self):
        """
        Return device info for Home Assistant device registry.
        """
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def available(self):
        """
        Return True if the channel is available and not marked as inactive.
        """
        channel = self._get_channel()
        if not channel or getattr(channel, 'temp', None) == 999.0:
            return False
        return True

    @property
    def state(self):
        """
        Estimate the time left (in minutes) until the channel reaches its max temperature.
        Uses a moving window of recent temperature readings to calculate the rate of change.
        Returns None if not enough data or if unavailable.
        """
        import time
        channel = self._get_channel()
        if not self.available:
            return None
        now = time.time()
        temp = getattr(channel, 'temp', None)
        # Add the current timestamp and temperature to the history
        self._history.append((now, temp))
        window_start = now - self._window_seconds
        # Only consider recent readings within the window
        recent = [x for x in self._history if x[0] >= window_start]
        if len(recent) < 2:
            return None
        dt = recent[-1][0] - recent[0][0]
        dtemp = recent[-1][1] - recent[0][1]
        if dt <= 0:
            return None
        rate_per_sec = dtemp / dt
        if rate_per_sec <= 0:
            return 0
        target = getattr(channel, 'max', None)
        if target is None:
            return None
        # Calculate time left in minutes
        time_left_min = (target - temp) / (rate_per_sec * 60)
        if time_left_min < 0:
            return 0
        return round(time_left_min, 2)

class WlanthermoSystemSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for system-level information (diagnostics, time, etc.).
    """
    def __init__(self, coordinator, device_name):
        """
        Initialize the system sensor entity.
        """
        super().__init__(coordinator)
        self._device_name = device_name
        self._attr_name = "System"
        self._attr_unique_id = f"{device_name}_system"
        self.entity_id = f"sensor.{device_name}_system"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def device_info(self):
        """
        Return device info for Home Assistant device registry.
        """
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def state(self):
        """
        Return the current system time value.
        """
        return getattr(self.coordinator.data.system, 'time', None)

    @property
    def extra_state_attributes(self):
        """
        Return additional system attributes for diagnostics.
        """
        sys = self.coordinator.data.system
        return {
            "time": getattr(sys, 'time', None),
            "unit": getattr(sys, 'unit', None),
            "soc": getattr(sys, 'soc', None),
            "charge": getattr(sys, 'charge', None),
            "rssi": getattr(sys, 'rssi', None),
            "online": getattr(sys, 'online', None),
        }

async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up all sensor entities for the WLANThermo integration.
    Dynamically creates entities for channels, pitmasters, system, and settings based on available data.
    """
    entry_id = config_entry.entry_id
    coordinator = hass.data[DOMAIN][entry_id]["coordinator"]
    device_name = config_entry.data.get("device_name", "WLANThermo")
    api = hass.data[DOMAIN][entry_id]["api"]

    entities = []
    import re
    safe_device_name = re.sub(r'[^a-zA-Z0-9_]', '_', device_name.lower())
    
    if coordinator.data is not None:
        # Add channel temperature and time left sensors for each channel
        num_channels = len(getattr(coordinator.data, 'channels', []))
        num_pitmasters = len(getattr(coordinator.data, 'pitmasters', []))
        for channel in getattr(coordinator.data, 'channels', []):
            entities.append(WlanthermoChannelTemperatureSensor(coordinator, channel))
            entities.append(WlanthermoChannelTimeLeftSensor(coordinator, channel))
        # Add pitmaster value sensors for each pitmaster
        for pitmaster in getattr(coordinator.data, 'pitmasters', []):
            entities.append(WlanthermoPitmasterValueSensor(coordinator, pitmaster, safe_device_name))
        # Add system-level diagnostic sensors if system object is present
        sys_obj = getattr(coordinator.data, 'system', None)
        if sys_obj:
            entities.append(WlanthermoSystemSensor(coordinator, safe_device_name))
            entities.append(WlanthermoSystemTimeSensor(coordinator, sys_obj, safe_device_name))
            entities.append(WlanthermoSystemUnitSensor(coordinator, sys_obj, safe_device_name))
            entities.append(WlanthermoSystemSocSensor(coordinator, sys_obj, safe_device_name))
            entities.append(WlanthermoSystemChargeSensor(coordinator, sys_obj, safe_device_name))
            entities.append(WlanthermoSystemRssiSensor(coordinator, sys_obj, safe_device_name))
            entities.append(WlanthermoSystemOnlineSensor(coordinator, sys_obj, safe_device_name))
        else:
            # Log a warning if system object is missing
            _LOGGER.warning(f"WLANThermo: coordinator.data.system is missing or falsy: {sys_obj!r}")
    else:
        # Log a warning if coordinator data is not yet available
        _LOGGER.warning("WLANThermo: coordinator.data is None. Entities will be unavailable until data is fetched.")

    # Add sensors for /settings endpoints if available
    settings = getattr(hass.data[DOMAIN][entry_id]["api"], "settings", None)
    if settings:
        if hasattr(settings, "device"):
            entities.append(WlanthermoDeviceInfoSensor(settings.device, safe_device_name))
        else:
            _LOGGER.warning("WLANThermo: /settings.device not found.")
        if hasattr(settings, "system"):
            entities.append(WlanthermoSystemInfoSensor(settings.system, safe_device_name))
            entities.append(WlanthermoSystemGetUpdateSensor(settings.system, safe_device_name))
        else:
            _LOGGER.warning("WLANThermo: /settings.system not found.")
        if hasattr(settings, "iot"):
            entities.append(WlanthermoIotInfoSensor(settings.iot, safe_device_name))
            entities.append(WlanthermoCloudLinkSensor(settings.iot, safe_device_name))
        else:
            _LOGGER.warning("WLANThermo: /settings.iot not found.")
    else:
        _LOGGER.warning("WLANThermo: /settings not found in API. No /settings sensors will be created.")

    # Add all created entities to Home Assistant
    import inspect
    if inspect.iscoroutinefunction(async_add_entities):
        hass.loop.create_task(async_add_entities(entities))
    else:
        async_add_entities(entities)

class WlanthermoSystemGetUpdateSensor(SensorEntity):
    """
    Sensor entity for system update availability (from /settings.system endpoint).
    """
    def __init__(self, system, device_name):
        """
        Initialize the system update sensor entity.
        """
        self._system = system
        self._attr_name = "System Update Available"
        self._attr_unique_id = f"{device_name}_system_getupdate"
        self.entity_id = f"sensor.{device_name}_system_getupdate"

    @property
    def device_info(self):
        entry_id = None
        hass = None
        if hasattr(self, 'coordinator') and hasattr(self.coordinator, 'config_entry'):
            entry_id = getattr(self.coordinator.config_entry, 'entry_id', None)
            hass = getattr(self.coordinator, 'hass', None)
        if not entry_id or not hass:
            try:
                import homeassistant.helpers.entity_platform
                platform = homeassistant.helpers.entity_platform.current_platform.get()
                hass = getattr(platform, 'hass', None)
                entry_id = getattr(platform, 'config_entry', None).entry_id if hasattr(platform, 'config_entry') else None
            except Exception:
                pass
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def state(self):
        """
        Return the update state: can be 'false' or a number (update available).
        """
        return getattr(self._system, "getupdate", None)

    @property
    def extra_state_attributes(self):
        """
        Return extra attributes for diagnostics (version, unit).
        """
        return {
            "version": getattr(self._system, "version", None),
            "unit": getattr(self._system, "unit", None),
        }

class WlanthermoCloudLinkSensor(SensorEntity):
    """
    Sensor entity for the cloud link (from /settings.iot endpoint).
    """
    def __init__(self, iot, device_name):
        """
        Initialize the cloud link sensor entity.
        """
        self._iot = iot
        self._attr_name = "Cloud Link"
        self._attr_unique_id = f"{device_name}_cloud_link"
        self.entity_id = f"sensor.{device_name}_cloud_link"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def device_info(self):
        entry_id = None
        hass = None
        if hasattr(self, 'coordinator') and hasattr(self.coordinator, 'config_entry'):
            entry_id = getattr(self.coordinator.config_entry, 'entry_id', None)
            hass = getattr(self.coordinator, 'hass', None)
        if not entry_id or not hass:
            try:
                import homeassistant.helpers.entity_platform
                platform = homeassistant.helpers.entity_platform.current_platform.get()
                hass = getattr(platform, 'hass', None)
                entry_id = getattr(platform, 'config_entry', None).entry_id if hasattr(platform, 'config_entry') else None
            except Exception:
                pass
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None
    
    @property
    def state(self):
        """
        Return the cloud link URL if enabled, including the API token if available.
        """
        if getattr(self._iot, "CLon", False):
            url = getattr(self._iot, "CLurl", None)
            token = getattr(self._iot, "CLtoken", None)
            if url and token:
                return f"{url}?api_token={token}"
            return url or None
        return None

    @property
    def available(self):
        """
        Return True if the cloud link is enabled.
        """
        return getattr(self._iot, "CLon", False)

    @property
    def extra_state_attributes(self):
        """
        Return extra attributes for diagnostics (cloud link status, URL, token).
        """
        return {
            "CLon": getattr(self._iot, "CLon", None),
            "CLurl": getattr(self._iot, "CLurl", None),
            "CLtoken": getattr(self._iot, "CLtoken", None),
        }
    
class WlanthermoSystemTimeSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for system time (diagnostic, from system object).
    """
    def __init__(self, coordinator, sys, device_name):
        """
        Initialize the system time sensor entity.
        """
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_translation_key = "system_time"
        self._attr_unique_id = f"{device_name}_system_time"
        self.entity_id = f"sensor.{device_name}_system_time"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def icon(self):
        return "mdi:clock"
    
    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def state(self):
        """
        Return the system time as a human-readable string (converted from unixtime).
        """
        import datetime
        system = getattr(self.coordinator.data, 'system', None)
        unixtime = getattr(system, 'time', None) if system else None
        if unixtime is None:
            return None
        try:
            # Accept both int and str
            ts = int(unixtime)
            return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(unixtime)

class WlanthermoSystemUnitSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._sys = sys
        self._attr_has_entity_name = True
        self._attr_translation_key = "temperature_unit"
        self._attr_unique_id = f"{device_name}_system_unit"
        self.entity_id = f"sensor.{device_name}_system_unit"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def icon(self):
        return "mdi:thermometer"
    
    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None
    
    @property
    def state(self):
        return getattr(self._sys, 'unit', None)

class WlanthermoSystemSocSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_translation_key = "battery_level"
        self._attr_unique_id = f"{device_name}_system_soc"
        self.entity_id = f"sensor.{device_name}_system_soc"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def icon(self):
        return "mdi:battery"
    
    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None
    
    @property
    def state(self):
        system = getattr(self.coordinator.data, 'system', None)
        return getattr(system, 'soc', None) if system else None

class WlanthermoSystemChargeSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_translation_key = "battery_charging"
        self._attr_unique_id = f"{device_name}_system_charge"
        self.entity_id = f"sensor.{device_name}_system_charge"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def icon(self):
        return "mdi:power-plug"
    
    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None
    
    @property
    def state(self):
        """
        Return the current battery charging state from the system object.
        Always fetches the latest value from coordinator.data.system.
        """
        system = getattr(self.coordinator.data, 'system', None)
        return getattr(system, 'charge', None) if system else None

class WlanthermoSystemRssiSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._attr_name = "Wlan RSSI"
        self._attr_unique_id = f"{device_name}_system_rssi"
        self.entity_id = f"sensor.{device_name}_system_rssi"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def icon(self):
        return "mdi:network"
    
    @property
    def device_info(self):
            entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
            hass = getattr(self.coordinator, 'hass', None)
            if hass and entry_id:
                return hass.data[DOMAIN][entry_id]["device_info"]
            return None
    
    @property
    def state(self):
        """
        Return the current WLAN RSSI value from the system object.
        """
        system = getattr(self.coordinator.data, 'system', None)
        return getattr(system, 'rssi', None) if system else None
    
class WlanthermoSystemOnlineSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, sys, device_name):
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_translation_key = "cloud_status"
        self._attr_unique_id = f"{device_name}_system_online"
        self.entity_id = f"sensor.{device_name}_system_online"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._translations = {}

    async def async_added_to_hass(self):
        """
        Called when entity is added to Home Assistant. Loads translations for online state.
        """
        await self._async_load_translations()

    async def _async_load_translations(self):
        """
        Load translation strings for the online state from the appropriate language file.
        Falls back to English if the selected language is not available.
        """
        import os, json

        hass = self.hass
        lang = getattr(hass.config, "language", "en")

        base = os.path.dirname(__file__)
        path = os.path.join(base, "translations", f"{lang}.json")

        if not os.path.exists(path):
            path = os.path.join(base, "translations", "en.json")

        def load(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)

        try:
            self._translations = await hass.async_add_executor_job(load, path)
        except Exception:
            self._translations = {}

    @property
    def icon(self):
        return "mdi:cloud"

    @property
    def device_info(self):
        entry_id = getattr(self.coordinator.config_entry, "entry_id", None)
        hass = getattr(self.coordinator, "hass", None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None
    
    @property
    def state(self):
        """
        Return the cloud connection state as a human-readable string using translations if available.
        """
        system = getattr(self.coordinator.data, "system", None)
        value = getattr(system, "online", None) if system else None

        default_map = {
            "0": "Not connected",
            "1": "Standby",
            "2": "Connected",
        }

        online_map = self._translations.get("system_online", default_map)

        return online_map.get(str(value), str(value))

class WlanthermoDeviceInfoSensor(SensorEntity):
    """
    Sensor entity for device information (from /settings.device endpoint).
    Reports device details such as serial, CPU, hardware/software version, etc.
    """
    def __init__(self, device, device_name):
        self._device = device
        self._attr_has_entity_name = True
        self._attr_translation_key = "device_info"
        self._attr_unique_id = f"{device_name}_device_info"
        self.entity_id = f"sensor.{device_name}_device_info"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def icon(self):
        return "mdi:information"
    @property
    def device_info(self):
            entry_id = None
            hass = None
            if hasattr(self, 'coordinator') and hasattr(self.coordinator, 'config_entry'):
                entry_id = getattr(self.coordinator.config_entry, 'entry_id', None)
                hass = getattr(self.coordinator, 'hass', None)
            if not entry_id or not hass:
                try:
                    import homeassistant.helpers.entity_platform
                    platform = homeassistant.helpers.entity_platform.current_platform.get()
                    hass = getattr(platform, 'hass', None)
                    entry_id = getattr(platform, 'config_entry', None).entry_id if hasattr(platform, 'config_entry') else None
                except Exception:
                    pass
            if hass and entry_id:
                return hass.data[DOMAIN][entry_id]["device_info"]
            return None
    
    @property
    def state(self):
        """
        Return the device name from the device info object.
        """
        return getattr(self._device, "device", None)

    @property
    def extra_state_attributes(self):
        """
        Return extra attributes for diagnostics (serial, cpu, flash size, versions, language).
        """
        return {
            "serial": getattr(self._device, "serial", None),
            "cpu": getattr(self._device, "cpu", None),
            "flash_size": getattr(self._device, "flash_size", None),
            "hw_version": getattr(self._device, "hw_version", None),
            "sw_version": getattr(self._device, "sw_version", None),
            "api_version": getattr(self._device, "api_version", None),
            "language": getattr(self._device, "language", None),
        }

class WlanthermoSystemInfoSensor(SensorEntity):
    """
    Sensor entity for system information (from /settings.system endpoint).
    Reports system details such as AP, host, language, update info, etc.
    """
    def __init__(self, system, device_name):
        self._system = system
        self._attr_name = "System Info"
        self._attr_unique_id = f"{device_name}_system_info"
        self.entity_id = f"sensor.{device_name}_system_info"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def icon(self):
        return "mdi:thermometer"

    @property
    def device_info(self):
        entry_id = None
        hass = None
        if hasattr(self, 'coordinator') and hasattr(self.coordinator, 'config_entry'):
            entry_id = getattr(self.coordinator.config_entry, 'entry_id', None)
            hass = getattr(self.coordinator, 'hass', None)
        if not entry_id or not hass:
            try:
                import homeassistant.helpers.entity_platform
                platform = homeassistant.helpers.entity_platform.current_platform.get()
                hass = getattr(platform, 'hass', None)
                entry_id = getattr(platform, 'config_entry', None).entry_id if hasattr(platform, 'config_entry') else None
            except Exception:
                pass
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None
    
    @property
    def state(self):
        """
        Return the system unit (e.g., temperature unit) from the system info object.
        """
        return getattr(self._system, "unit", None)

    @property
    def extra_state_attributes(self):
        """
        Return extra attributes for diagnostics (AP, host, language, update info).
        """
        return {
            "ap": getattr(self._system, "ap", None),
            "host": getattr(self._system, "host", None),
            "language": getattr(self._system, "language", None),
            "getupdate": getattr(self._system, "getupdate", None),
            "autoupd": getattr(self._system, "autoupd", None),
        }

class WlanthermoIotInfoSensor(SensorEntity):
    """
    Sensor entity for IoT/cloud information (from /settings.iot endpoint).
    Reports cloud URL and related details.
    """
    def __init__(self, iot, device_name):
        self._iot = iot
        self._attr_name = "Cloud URL"
        self._attr_unique_id = f"{device_name}_cloud_url"
        self.entity_id = f"sensor.{device_name}_cloud_url"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def state(self):
        """
        Return the cloud URL from the IoT info object.
        """
        return getattr(self._iot, "CLurl", None)

    @property
    def extra_state_attributes(self):
        """
        Return extra attributes for diagnostics (cloud URL).
        """
        return {
            "cloud_url": getattr(self._iot, "CLurl", None),
        }

class WlanthermoChannelSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for a channel, reporting temperature and channel details.
    """
    def __init__(self, coordinator, channel, device_name):
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_translation_key = "channel"
        self._channel = channel
        self._device_name = device_name
        self._attr_unique_id = f"{device_name}_channel_{channel.number}"
        self.entity_id = f"sensor.{device_name}_channel_{channel.number}"

    @property
    def device_info(self):
        """
        Return device info for Home Assistant device registry.
        """
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def state(self):
        """
        Return the current temperature value for this channel.
        """
        return self._channel.temp

    @property
    def extra_state_attributes(self):
        """
        Return extra attributes for diagnostics (channel details).
        """
        return {
            "number": self._channel.number,
            "name": self._channel.name,
            "typ": self._channel.typ,
            "temp": self._channel.temp,
            "min": self._channel.min,
            "max": self._channel.max,
            "alarm": self._channel.alarm,
            "color": self._channel.color,
            "fixed": self._channel.fixed,
            "connected": self._channel.connected,
        }

class WlanthermoPitmasterSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for pitmaster, reporting pitmaster value and details.
    """
    def __init__(self, coordinator, pitmaster, device_name, idx):
        super().__init__(coordinator)
        self._pitmaster = pitmaster
        self._device_name = device_name
        self._attr_name = f"Pitmaster {idx}"
        self._attr_unique_id = f"{device_name}_pitmaster_{idx}"
        self.entity_id = f"sensor.{device_name}_pitmaster_{idx}"

    @property
    def device_info(self):
        """
        Return device info for Home Assistant device registry.
        """
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def state(self):
        """
        Return the current pitmaster value.
        """
        return self._pitmaster.value

    @property
    def extra_state_attributes(self):
        """
        Return extra attributes for diagnostics (pitmaster details).
        """
        return {
            "id": self._pitmaster.id,
            "channel": self._pitmaster.channel,
            "pid": self._pitmaster.pid,
            "value": self._pitmaster.value,
            "set": self._pitmaster.set,
            "typ": self._pitmaster.typ,
            "set_color": self._pitmaster.set_color,
            "value_color": self._pitmaster.value_color,
        }
    
class WlanthermoPitmasterValueSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for pitmaster value, reporting the current value for a pitmaster.
    """
    def __init__(self, coordinator, pitmaster, device_name):
        super().__init__(coordinator)
        self._pitmaster_id = pitmaster.id
        self._attr_has_entity_name = True
        self._attr_translation_key = "pitmaster_value"
        self._attr_translation_placeholders = {"pitmaster_id": str(pitmaster.id)}
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_unique_id = f"{safe_device_name}_pitmaster_{pitmaster.id}_value"
        self.entity_id = f"sensor.{safe_device_name}_pitmaster_{pitmaster.id}_value"
        self._attr_icon = "mdi:fan"
        self._attr_native_unit_of_measurement = "%"

    def _get_pitmaster(self):
        """
        Helper to get the current pitmaster object from the coordinator data.
        """
        pitmasters = getattr(self.coordinator.data, 'pitmasters', [])
        for pm in pitmasters:
            if pm.id == self._pitmaster_id:
                return pm
        return None

    @property
    def device_info(self):
        """
        Return device info for Home Assistant device registry.
        """
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def state(self):
        """
        Return the current value for this pitmaster, or None if not found.
        """
        pitmaster = self._get_pitmaster()
        return getattr(pitmaster, "value", None) if pitmaster else None
