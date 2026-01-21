"""
Sensor platform for WLANThermo
Exposes system, channel, pitmaster, and temperature sensors as Home Assistant entities.
Includes diagnostic and device info sensors.
"""

from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
    UnitOfTime,
)

from homeassistant.core import callback
from .const import DOMAIN
from datetime import timedelta, datetime
from .data import WlanthermoData
import logging
import collections

async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up all sensor entities for the WLANThermo integration.
    Dynamically creates entities for channels, pitmasters, system, and settings based on available data.
    """
    entry_id = config_entry.entry_id
    entry_data = hass.data[DOMAIN][entry_id]
    entity_store = entry_data.setdefault("entities", {})
    entity_store.setdefault("channels", set())
    entity_store.setdefault("pitmasters", set())
    entity_store.setdefault("system", set())
    entity_store.setdefault("settings", set())

    coordinator = entry_data["coordinator"]
    api = entry_data["api"]

    async def _async_discover_entities():
        if not coordinator.data:
            return
        new_entities = []

        # Channels
        for channel in coordinator.data.channels:
            ch_id = channel.number

            if ch_id not in entity_store["channels"]:
                new_entities.extend([
                    WlanthermoChannelTemperatureSensor(coordinator, ch_id, entry_data),
                    WlanthermoChannelTimeLeftSensor(coordinator, ch_id, entry_data),
                ])
                entity_store["channels"].add(ch_id)

        # Pitmasters
        for pitmaster in coordinator.data.pitmasters:
            pm_id = pitmaster.id

            if pm_id not in entity_store["pitmasters"]:
                new_entities.extend([
                    WlanthermoPitmasterValueSensor(coordinator, pitmaster, entry_data),
                    WlanthermoPitmasterTemperatureSensor(coordinator, pitmaster, entry_data),
                ])
                entity_store["pitmasters"].add(pm_id)

        # System sensors
        system = getattr(coordinator.data, "system", None)
        if system and not entity_store["system"]:
            new_entities.extend([
                WlanthermoSystemSensor(coordinator, entry_data),
                WlanthermoSystemTimeSensor(coordinator, entry_data),
                WlanthermoSystemUnitSensor(coordinator, entry_data),
                WlanthermoSystemSocSensor(coordinator, entry_data),
                WlanthermoSystemChargeSensor(coordinator, entry_data),
                WlanthermoSystemRssiSensor(coordinator, entry_data),
                WlanthermoCloudOnlineSensor(coordinator, entry_data),
            ])
            entity_store["system"].add("system")

        # Settings sensors (NUR wenn coordinator.data vorhanden ist!)
        settings = getattr(api, "settings", None)
        if settings and not entity_store["settings"]:
            if hasattr(settings, "device"):
                new_entities.append(WlanthermoDeviceInfoSensor(coordinator, entry_data))
            if hasattr(settings, "system"):
                new_entities.extend([
                    WlanthermoSystemInfoSensor(coordinator, entry_data),
                    WlanthermoSystemGetUpdateSensor(coordinator, entry_data),
                ])
            if hasattr(settings, "iot"):
                new_entities.extend([
                    WlanthermoCloudLinkSensor(coordinator, entry_data),
                ])

            entity_store["settings"].add("settings")

        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_async_discover_entities)
    await _async_discover_entities()


class WlanthermoChannelTemperatureSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for a channel's temperature.
    Reports the current temperature for each channel.
    """
    def __init__(self, coordinator, channel_number: int, entry_data):
        super().__init__(coordinator)
        self._channel_number = channel_number
        self._attr_has_entity_name = True
        self._attr_translation_key = "channel_temperature"
        self._attr_translation_placeholders = {"channel_number": str(channel_number)}
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_channel_{channel_number}_temperature"
        )
        self._attr_icon = "mdi:thermometer"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_info = entry_data["device_info"]

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        if not self.coordinator.data:
            return None
        
        for ch in self.coordinator.data.channels:
            if ch.number == self._channel_number:
                return ch
        return None

    @property
    def native_value(self):
        """
        Return the current temperature value, or None if sensor is not connected (999.0).
        """
        channel = self._get_channel()
        if not channel:
            return None
        temp = getattr(channel, "temp", None)
        if temp is None:
            return None  # No temperature data available

        show_inactive = self.coordinator.config_entry.options.get(
            "show_inactive_unavailable",
            self.coordinator.config_entry.data.get(
                "show_inactive_unavailable", True
            )
        )
        if temp == 999.0 and show_inactive:
            return None
        return temp
    
    @property
    def available(self):
        """
        Return True if the device is online and the channel is available and not marked as inactive.
        """
        if not self.coordinator.last_update_success:
            return False

        system = getattr(self.coordinator.data, "system", None)
        if system is None:
            return False

        channel = self._get_channel()
        if not channel:
            return False
        show_inactive = (
            self.coordinator.config_entry.options.get(
                "show_inactive_unavailable",
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
    def __init__(self, coordinator, channel_number: int, entry_data, window_seconds=300):
        super().__init__(coordinator)
        self._channel_number = channel_number
        self._window_seconds = window_seconds
        self._history = collections.deque(maxlen=60)

        self._attr_device_info = entry_data["device_info"]
        self._attr_has_entity_name = True
        self._attr_translation_key = "channel_time_left"
        self._attr_translation_placeholders = {"channel_number": str(channel_number)}
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_channel_{channel_number}_timeleft"
        )
        self._attr_icon = "mdi:timer"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        if not self.coordinator.data:
            return None
        
        for ch in self.coordinator.data.channels:
            if ch.number == self._channel_number:
                return ch
        return None
    
    @property
    def native_value(self) -> float | None:
        """
        Estimate the time left (in minutes) until the channel reaches its max temperature.
        Uses a moving window of recent temperature readings to calculate the rate of change.
        """
        import time
        channel = self._get_channel()
        if not self.available or not channel:
            return None

        now = time.time()
        temp = getattr(channel, "temp", None)
        if temp is None:
            return None

        # Add current reading to history
        self._history.append((now, temp))
        window_start = now - self._window_seconds

        # Only consider readings within the time window
        recent = [x for x in self._history if x[0] >= window_start]
        if len(recent) < 2:
            return None

        dt = recent[-1][0] - recent[0][0]
        dtemp = recent[-1][1] - recent[0][1]
        if dt <= 0 or dtemp <= 0:
            return 0

        rate_per_sec = dtemp / dt
        target = getattr(channel, "max", None)
        if target is None:
            return None

        # Time left in minutes
        time_left_min = (target - temp) / (rate_per_sec * 60)
        return round(max(time_left_min, 0), 2)

    
    @property
    def available(self):
        """
        Return True if the device is online and the channel is available and not marked as inactive.
        """
        if not self.coordinator.last_update_success:
            return False

        system = getattr(self.coordinator.data, "system", None)
        if system is None:
            return False

        channel = self._get_channel()
        if not channel:
            return False
        show_inactive = (
            self.coordinator.config_entry.options.get(
                "show_inactive_unavailable",
                self.coordinator.config_entry.data.get("show_inactive_unavailable", True)
            )
        )
        temp = getattr(channel, "temp", None)
        if temp == 999.0 and show_inactive:
            return False
        return True


class WlanthermoSystemSensor(CoordinatorEntity, SensorEntity):
    """Overall system online/offline state."""

    _attr_has_entity_name = True
    _attr_translation_key = "system_status"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["offline", "online"]

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_system_status"
        self._attr_device_info = entry_data["device_info"]

    @property
    def native_value(self) -> str:
        if not self.coordinator.last_update_success:
            return "offline"

        system = getattr(self.coordinator.data, "system", None)
        if not system:
            return "offline"

        return "online"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def icon(self):
        return (
            "mdi:lan-connect"
            if self.native_value == "online"
            else "mdi:lan-disconnect"
        )

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return None

        system = getattr(self.coordinator.data, "system", None)
        if not system:
            return None

        return {
            "time": getattr(system, "time", None),
            "unit": getattr(system, "unit", None),
            "soc": getattr(system, "soc", None),
            "charge": getattr(system, "charge", None),
            "rssi": getattr(system, "rssi", None),
            "online": getattr(system, "online", None),
        }

class WlanthermoSystemGetUpdateSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for system update availability (from /settings.system).
    """

    _attr_has_entity_name = True
    _attr_translation_key = "system_update"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:cellphone-arrow-down"

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_system_getupdate"
        self._attr_device_info = entry_data["device_info"]

    @property
    def _system(self):
        """
        Return current settings.system from API (not coordinator.data).
        """
        hass = self.coordinator.hass
        entry_id = self.coordinator.config_entry.entry_id

        api = hass.data[DOMAIN][entry_id]["api"]
        settings = getattr(api, "settings", None)

        return getattr(settings, "system", None) if settings else None

    @property
    def native_value(self) -> str | int | None:
        """
        Returns:
        - None / False → no update available
        - str / int → update available
        """
        system = self._system
        return getattr(system, "getupdate", None) if system else None

    @property
    def extra_state_attributes(self):
        system = self._system
        if not system:
            return {}

        return {
            "version": getattr(system, "version", None),
            "autoupdate": getattr(system, "autoupd", None),
        }

    @property
    def available(self) -> bool:
        """
        Sensor is available when device is reachable and system settings exist.
        """
        return self.coordinator.last_update_success and self._system is not None


class WlanthermoCloudLinkSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for the cloud link (from /settings.iot).
    """

    _attr_has_entity_name = True
    _attr_translation_key = "cloud_link"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:link"

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_cloud_link"
        self._attr_device_info = entry_data["device_info"]

    @property
    def _iot(self):
        data = self.coordinator.data
        if not data or not getattr(data, "settings", None):
            return None
        return getattr(data.settings, "iot", None)
    
    @property
    def native_value(self) -> str | None:
        """
        Return the cloud link URL if enabled.
        """
        iot = self._iot
        if not iot or not getattr(iot, "CLon", False):
            return None

        url = getattr(iot, "CLurl", None)
        token = getattr(iot, "CLtoken", None)

        if url and token:
            return f"{url}?api_token={token}"

        return url
    
    @property
    def available(self):
        """
        Return True if the cloud link is enabled.
        """
        if not self.coordinator.last_update_success:
            return False

        system = getattr(self.coordinator.data, "system", None)
        if not system:
            return False

        return getattr(system, "online", None) == 2
    
    
class WlanthermoSystemTimeSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for system time (diagnostic, from system object).
    """
    _attr_has_entity_name = True
    _attr_translation_key = "system_time"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    #_attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock"

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_system_time"
        self._attr_device_info = entry_data["device_info"]

    @property
    def native_value(self):
        system = getattr(self.coordinator.data, 'system', None)
        if not system:
            return None
        
        unixtime = getattr(system, 'time', None)
        if unixtime is None:
            return None
        
        try:
            # Accept both int and str
            ts = int(unixtime)
            return datetime.fromtimestamp(ts).strftime("%H:%M:%S %d.%m.%Y")
            # return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            return str(unixtime)

    @property
    def available(self):
        """
        Return True if the device is online.
        """
        return self.coordinator.last_update_success


class WlanthermoSystemUnitSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for temperature unit (°C / °F).
    """

    _attr_has_entity_name = True
    _attr_translation_key = "temperature_unit"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:thermometer"
    _attr_options = ["C", "F"]

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_system_unit"
        self._attr_device_info = entry_data["device_info"]

    @property
    def native_value(self) -> str | None:
        system = getattr(self.coordinator.data, "system", None)
        if not system:
            return None

        unit = getattr(system, "unit", None)
        if unit in self._attr_options:
            return unit

        return None

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

class WlanthermoSystemSocSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for battery state of charge (SoC).
    """

    _attr_has_entity_name = True
    _attr_translation_key = "battery_level"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_system_soc"
        self._attr_device_info = entry_data["device_info"]

    @property
    def native_value(self) -> int | None:
        system = getattr(self.coordinator.data, "system", None)
        soc = getattr(system, "soc", None) if system else None

        try:
            return int(soc) if soc is not None else None
        except (ValueError, TypeError):
            return None

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
    
class WlanthermoSystemChargeSensor(CoordinatorEntity, BinarySensorEntity):
    """
    Binary sensor indicating whether the battery is currently charging.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "battery_charging"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_system_charge"
        self._attr_device_info = entry_data["device_info"]

    @property
    def is_on(self) -> bool | None:
        """
        Return True if the battery is charging.
        """
        system = getattr(self.coordinator.data, "system", None)
        charge = getattr(system, "charge", None) if system else None

        if charge is None:
            return None

        return bool(charge)

    @property
    def icon(self) -> str:
        system = getattr(self.coordinator.data, "system", None)
        soc = getattr(system, "soc", None) if system else None
        
        if self.is_on is None:
            return "mdi:battery-unknown"
        if self.is_on:
            return "mdi:battery-charging"
        if soc == 100:
            return "mdi:power-plug-battery"
        return "mdi:battery-medium"
    
    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success


class WlanthermoSystemRssiSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for WLAN RSSI (signal strength in dBm).
    """

    _attr_has_entity_name = True
    _attr_translation_key = "wifi_signal"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "dBm"

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_system_rssi"
        self._attr_device_info = entry_data["device_info"]

    @property
    def native_value(self) -> int | None:
        """
        Return the current WLAN RSSI value (negative dBm).
        """
        system = getattr(self.coordinator.data, "system", None)
        rssi = getattr(system, "rssi", None) if system else None

        if rssi is None:
            return None

        try:
            return int(rssi)
        except (TypeError, ValueError):
            return None

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
    

class WlanthermoCloudOnlineSensor(CoordinatorEntity, SensorEntity):
    """
    Reports the WLANThermo Cloud online state (0/1/2) as ENUM.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "cloud_status"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["not_connected", "standby", "connected"]

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_cloud_status"
        self._attr_device_info = entry_data["device_info"]

    @property
    def native_value(self) -> str | None:
        system = getattr(self.coordinator.data, "system", None)
        if not system:
            return None

        value = getattr(system, "online", None)
        try:
            return {
                0: "not_connected",
                1: "standby",
                2: "connected",
            }.get(int(value))
        except (TypeError, ValueError):
            return None

    @property
    def icon(self) -> str:
        """
        Dynamic icon based on cloud connection state.
        """
        match self.native_value:
            case "connected":
                return "mdi:cloud-check-variant-outline"
            case "standby":
                return "mdi:cloud-outline"
            case "not_connected":
                return "mdi:cloud-off"
            case _:
                return "mdi:cloud-question-outline"
     
    @property
    def extra_state_attributes(self):
        """
        Additional IoT diagnostics.
        """
        api = getattr(self.coordinator, "api", None)
        settings = getattr(api, "settings", None) if api else None
        iot = getattr(settings, "iot", None) if settings else None

        if not iot:
            return {}

        return {
            "cloud_enabled": getattr(iot, "CLon", None),
            "cloud_url": getattr(iot, "CLurl", None),
            "cloud_interval": getattr(iot, "CLint", None),
            "mqtt_enabled": getattr(iot, "PMQon", None),
            "mqtt_host": getattr(iot, "PMQhost", None),
            "mqtt_port": getattr(iot, "PMQport", None),
            "mqtt_qos": getattr(iot, "PMQqos", None),
            "mqtt_interval": getattr(iot, "PMQint", None),
        }
           
    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
    

class WlanthermoDeviceInfoSensor(CoordinatorEntity, SensorEntity):
    """
    Diagnostic sensor exposing WLANThermo device information
    from /settings.device.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "device_info"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:information"

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_device_info"
        self._attr_device_info = entry_data["device_info"]

    @property
    def _device(self):
        """
        Always return the current settings.device object.
        """
        api = self.coordinator.hass.data[DOMAIN][
            self.coordinator.config_entry.entry_id
        ].get("api")

        settings = getattr(api, "settings", None)
        return getattr(settings, "device", None) if settings else None

    @property
    def native_value(self) -> str | None:
        """
        Use the device model/name as main state.
        """
        device = self._device
        return getattr(device, "device", None) if device else None

    @property
    def extra_state_attributes(self):
        """
        Full diagnostic payload.
        """
        device = self._device
        if not device:
            return {}

        return {
            "serial": getattr(device, "serial", None),
            "cpu": getattr(device, "cpu", None),
            "flash_size": getattr(device, "flash_size", None),
            "hw_version": getattr(device, "hw_version", None),
            "sw_version": getattr(device, "sw_version", None),
            "api_version": getattr(device, "api_version", None),
            "language": getattr(device, "language", None),
        }

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success


class WlanthermoSystemInfoSensor(CoordinatorEntity, SensorEntity):
    """
    Diagnostic sensor exposing system information
    from /settings.system.
    """
    _attr_has_entity_name = True
    _attr_translation_key = "system_info"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:cog-outline"

    def __init__(self, coordinator, entry_data):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_system_info"
        self._attr_device_info = entry_data["device_info"]

    @property
    def _system(self):
        """
        Always return the current settings.system object.
        """
        api = self.coordinator.hass.data[DOMAIN][
            self.coordinator.config_entry.entry_id
        ].get("api")

        settings = getattr(api, "settings", None)
        return getattr(settings, "system", None) if settings else None

    @property
    def native_value(self) -> str | None:
        """
        Use host as primary state (informational).
        """
        system = self._system
        return getattr(system, "host", None) if system else None

    @property
    def extra_state_attributes(self):
        """
        Full diagnostic payload.
        """
        system = self._system
        if not system:
            return {}

        return {
            "ap": getattr(system, "ap", None),
            "unit": getattr(system, "unit", None),
            "language": getattr(system, "language", None),
            "version": getattr(system, "version", None),
            "getupdate": getattr(system, "getupdate", None),
            "autoupd": getattr(system, "autoupd", None),
            "prerelease": getattr(system, "prerelease", None),
            "hwversion": getattr(system, "hwversion", None),
        }

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success


# class WlanthermoIotInfoSensor(CoordinatorEntity, SensorEntity):
#     """
#     Diagnostic sensor exposing IoT / cloud information
#     from /settings.iot.
#     """
#     _attr_has_entity_name = True
#     _attr_translation_key = "cloud_url"
#     _attr_entity_category = EntityCategory.DIAGNOSTIC
#     _attr_icon = "mdi:cloud-outline"

#     def __init__(self, coordinator, entry_data):
#         super().__init__(coordinator)
#         self._attr_unique_id = f"{coordinator.config_entry.entry_id}_cloud_url"
#         self._attr_device_info = entry_data["device_info"]

#     @property
#     def _iot(self):
#         """
#         Always return current settings.iot from the API.
#         """
#         api = self.coordinator.hass.data[DOMAIN][
#             self.coordinator.config_entry.entry_id
#         ].get("api")

#         settings = getattr(api, "settings", None)
#         return getattr(settings, "iot", None) if settings else None

#     @property
#     def native_value(self) -> str | None:
#         """
#         Return the configured cloud URL (if any).
#         """
#         iot = self._iot
#         return getattr(iot, "CLurl", None) if iot else None

#     @property
#     def available(self) -> bool:
#         return self.coordinator.last_update_success

    
class WlanthermoChannelSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for a channel temperature.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "channel"

    def __init__(self, coordinator, channel, entry_data):
        super().__init__(coordinator)
        self._channel_number = channel.number
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_channel_{channel.number}"
        self._attr_device_info = entry_data["device_info"]

    def _get_channel(self):
        channels = getattr(self.coordinator.data, "channels", [])
        for ch in channels:
            if ch.number == self._channel_number:
                return ch
        return None

    @property
    def native_value(self) -> float | None:
        ch = self._get_channel()
        return getattr(ch, "temp", None) if ch else None

    @property
    def extra_state_attributes(self):
        ch = self._get_channel()
        if not ch:
            return {}

        return {
            "number": ch.number,
            "name": ch.name,
            "type": ch.typ,
            "min": ch.min,
            "max": ch.max,
            "alarm": ch.alarm,
            "color": ch.color,
            "fixed": ch.fixed,
            "connected": ch.connected,
        }

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False

        if not getattr(self.coordinator.data, "system", None):
            return False

        return self._get_channel() is not None


class WlanthermoPitmasterSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for pitmaster value.
    """

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, pitmaster, idx, entry_data):
        super().__init__(coordinator)
        self._pitmaster_id = pitmaster.id
        self._attr_name = f"Pitmaster {idx}"
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_pitmaster_{idx}"
        self._attr_device_info = entry_data["device_info"]
    def _get_pitmaster(self):
        pitmasters = getattr(self.coordinator.data, "pitmasters", [])
        for pm in pitmasters:
            if pm.id == self._pitmaster_id:
                return pm
        return None

    @property
    def native_value(self) -> float | None:
        pm = self._get_pitmaster()
        return getattr(pm, "value", None) if pm else None

    @property
    def extra_state_attributes(self):
        pm = self._get_pitmaster()
        if not pm:
            return {}

        return {
            "id": pm.id,
            "channel": pm.channel,
            "pid": pm.pid,
            "set": pm.set,
            "type": pm.typ,
            "set_color": pm.set_color,
            "value_color": pm.value_color,
        }

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False

        if not getattr(self.coordinator.data, "system", None):
            return False

        return self._get_pitmaster() is not None

    
class WlanthermoPitmasterValueSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for pitmaster value.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "pitmaster_value"
    _attr_icon = "mdi:fan"
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, pitmaster, entry_data):
        super().__init__(coordinator)
        self._pitmaster_id = pitmaster.id
        self._attr_translation_placeholders = {
            "pitmaster_number": str(pitmaster.id + 1)
        }
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_pitmaster_{pitmaster.id}_value"
        )
        self._attr_device_info = entry_data["device_info"]

    def _get_pitmaster(self):
        for pm in getattr(self.coordinator.data, "pitmasters", []):
            if pm.id == self._pitmaster_id:
                return pm
        return None

    @property
    def native_value(self) -> float | None:
        pm = self._get_pitmaster()
        return getattr(pm, "value", None) if pm else None

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        return self._get_pitmaster() is not None


class WlanthermoPitmasterTemperatureSensor(CoordinatorEntity, SensorEntity):
    """
    Sensor entity for a pitmaster's temperature.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "pitmaster_temperature"
    _attr_icon = "mdi:thermometer"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, pitmaster, entry_data):
        super().__init__(coordinator)
        self._pitmaster_id = pitmaster.id
        self._attr_translation_placeholders = {
            "pitmaster_number": str(pitmaster.id +1)
        }
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_pitmaster_{pitmaster.id}_temperature"
        )
        self._attr_device_info = entry_data["device_info"]

    def _get_channel(self):
        pitmasters = getattr(self.coordinator.data, "pitmasters", [])
        pm = next((p for p in pitmasters if p.id == self._pitmaster_id), None)
        if not pm:
            return None

        channels = getattr(self.coordinator.data, "channels", [])
        return next(
            (ch for ch in channels if ch.number == pm.channel),
            None,
        )

    @property
    def native_value(self):
        ch = self._get_channel()
        if not ch:
            return None

        temp = getattr(ch, "temp", None)
        if temp == 999.0:
            return None

        return temp

    @property
    def native_unit_of_measurement(self):
        system = getattr(self.coordinator.data, "system", None)
        return (
            UnitOfTemperature.FAHRENHEIT
            if getattr(system, "unit", None) == "F"
            else UnitOfTemperature.CELSIUS
        )
    
    @property
    def available(self):
        """
        Return True if coordinator updated successfully and
        the pitmaster's associated channel exists.
        """
        if not self.coordinator.last_update_success:
            return False

        system = getattr(self.coordinator.data, "system", None)
        if system is None:
            return False

        channel = self._get_channel()
        if channel is None:
            return False

        # optional: hide inactive channel (999.0)
        if getattr(channel, "temp", None) in (None, 999.0):
            return False

        return True

