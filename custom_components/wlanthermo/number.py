"""
Number platform for WLANThermo adjustable values.
Exposes min/max temperature and pitmaster values as Home Assistant number entities.
"""

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

CHANNEL_NUMBER_FIELDS = [
    # Defines which channel fields are exposed as number entities
    {
        "key": "min",
        "name": "Min Temperature",
        "icon": "mdi:thermometer-low",
        "min": -30.0,
        "max": 999.9,
        "step": 0.1,
        "unit": "°C",
    },
    {
        "key": "max",
        "name": "Max Temperature",
        "icon": "mdi:thermometer-high",
        "min": -30.0,
        "max": 999.9,
        "step": 0.1,
        "unit": "°C",
    },
]

PITMASTER_NUMBER_FIELDS = [
    # Defines which pitmaster fields are exposed as number entities
    {
        "key": "value",
        "name": "Pitmaster Value",
        "icon": "mdi:fan",
        "min": 0,
        "max": 100,
        "step": 1,
        "unit": "%",
    },
    {
        "key": "set",
        "name": "Set Temperature",
        "icon": "mdi:target",
        "min": 0.0,
        "max": 999.9,
        "step": 0.1,
        "unit": "°C",
    },
]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up number entities for each channel and pitmaster in the config entry.
    """
    entry_id = config_entry.entry_id
    entry_data = hass.data[DOMAIN][entry_id]
    coordinator = entry_data["coordinator"]
    if coordinator.data is None:
        return

    data = coordinator.data
    channels = getattr(data, "channels", []) if data else []
    pitmasters = getattr(data, "pitmasters", []) if data else []

    entities = []

    for channel in channels:
        for field in CHANNEL_NUMBER_FIELDS:
            entities.append(
                WlanthermoChannelNumber(coordinator, channel, field, entry_data)
            )

    for pitmaster in pitmasters:
        for field in PITMASTER_NUMBER_FIELDS:
            entities.append(
                WlanthermoPitmasterNumber(coordinator, pitmaster, field, entry_data)
            )

    async_add_entities(entities)

class WlanthermoChannelNumber(CoordinatorEntity, NumberEntity):
    """
    Number entity for a channel's min/max temperature.
    Allows user to set min/max values for each channel.
    """
    def __init__(self, coordinator, channel, field, entry_data):
        super().__init__(coordinator)
        self._channel_number = channel.number
        self._field = field
        self._api = coordinator.hass.data[DOMAIN][
            coordinator.config_entry.entry_id
        ]["api"]

        self._attr_has_entity_name = True
        self._attr_translation_key = f"channel_{field['key']}"
        self._attr_translation_placeholders = {
            "channel_number": str(channel.number)
        }

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_"
            f"channel_{channel.number}_{field['key']}"
        )

        self._attr_icon = field["icon"]
        self._attr_native_min_value = field["min"]
        self._attr_native_max_value = field["max"]
        self._attr_native_step = field["step"]
        self._attr_native_unit_of_measurement = field["unit"]
        self._attr_device_info = entry_data["device_info"]


    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        channels = getattr(self.coordinator.data, 'channels', [])
        for ch in channels:
            if ch.number == self._channel_number:
                return ch
        return None

    async def async_set_native_value(self, value):
        channel = self._get_channel()
        if not channel:
            return

        channel_data = {
            "number": channel.number,
            "name": channel.name,
            "typ": channel.typ,
            "temp": channel.temp,
            "min": value if self._field["key"] == "min" else channel.min,
            "max": value if self._field["key"] == "max" else channel.max,
            "alarm": channel.alarm,
            "color": channel.color,
        }

        await self._api.async_set_channel(channel_data)
        await self.coordinator.async_request_refresh()

    @property
    def native_value(self):
        """
        Return the current value of the field for this channel.
        """
        channel = self._get_channel()
        return getattr(channel, self._field["key"], None) if channel else None
    
    @property
    def available(self):
        return self.coordinator.last_update_success


class WlanthermoPitmasterNumber(CoordinatorEntity, NumberEntity):
    """
    Number entity for a pitmaster's value or set temperature.
    """
    def __init__(self, coordinator, pitmaster, field, entry_data):
        super().__init__(coordinator)

        self._pitmaster_id = pitmaster.id
        self._field = field

        self._attr_has_entity_name = True
        self._attr_translation_key = f"pitmaster_{field['key']}"
        self._attr_translation_placeholders = {
            "pitmaster_number": str(pitmaster.id + 1)
        }

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_"
            f"pitmaster_{pitmaster.id}_{field['key']}"
        )

        self._attr_icon = field["icon"]
        self._attr_native_min_value = field["min"]
        self._attr_native_max_value = field["max"]
        self._attr_native_step = field["step"]
        self._attr_native_unit_of_measurement = field["unit"]
        self._attr_device_info = entry_data["device_info"]


    def _get_pitmaster(self):
        """
        Helper to get the current pitmaster object from the coordinator data.
        """
        pitmasters = getattr(self.coordinator.data, 'pitmasters', [])
        for pm in pitmasters:
            if pm.id == self._pitmaster_id:
                return pm
        return None

    async def async_set_native_value(self, value):
        """
        Set the value for this pitmaster field and update via API.
        """
        import logging
        _LOGGER = logging.getLogger(__name__)
        pitmaster = self._get_pitmaster()
        if not pitmaster:
            _LOGGER.error(f"[WLANThermo] PitmasterNumber: Pitmaster {self._pitmaster_id} not found for set_native_value")
            return
        #_LOGGER.warning(f"[WLANThermo] PitmasterNumber: Setting {self._field['key']} for pitmaster {pitmaster.id} to {value}")
        pitmaster_data = {
            "id": pitmaster.id,
            "channel": pitmaster.channel,
            "pid": pitmaster.pid,
            "value": value if self._field["key"] == "value" else pitmaster.value,
            "set": value if self._field["key"] == "set" else pitmaster.set,
            "typ": pitmaster.typ,
        }
        #_LOGGER.warning(f"[WLANThermo] PitmasterNumber: Sending to API: {pitmaster_data}")
        result = await self._api.async_set_pitmaster(pitmaster_data)
        #_LOGGER.warning(f"[WLANThermo] PitmasterNumber: API result: {result}")
        await self.coordinator.async_request_refresh()

    @property
    def native_value(self):
        """
        Return the current value of the field for this pitmaster.
        """
        pitmaster = self._get_pitmaster()
        return getattr(pitmaster, self._field["key"], None) if pitmaster else None
    
    @property
    def available(self):
        return self.coordinator.last_update_success
