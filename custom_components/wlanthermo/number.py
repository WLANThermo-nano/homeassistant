"""Number platform for WLANThermo BBQ adjustable values."""

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

CHANNEL_NUMBER_FIELDS = [
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
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities = []
    # Channel numbers
    for channel in coordinator.data.channels:
        for field in CHANNEL_NUMBER_FIELDS:
            entities.append(WlanthermoChannelNumber(coordinator, channel, field))
    # Pitmaster numbers
    for pitmaster in coordinator.data.pitmasters:
        for field in PITMASTER_NUMBER_FIELDS:
            entities.append(WlanthermoPitmasterNumber(coordinator, pitmaster, field))
    async_add_entities(entities)

class WlanthermoChannelNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, channel, field):
        super().__init__(coordinator)
        self._channel_number = channel.number
        self._field = field
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo_BBQ")
            else:
                device_name = "WLANThermo_BBQ"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Channel {channel.number} {field['name']}"
        self._attr_unique_id = f"{safe_device_name}_channel_{channel.number}_{field['key']}"
        self.entity_id = f"number.{safe_device_name}_channel_{channel.number}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_native_min_value = field["min"]
        self._attr_native_max_value = field["max"]
        self._attr_native_step = field["step"]
        self._attr_native_unit_of_measurement = field["unit"]
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    def _get_channel(self):
        channels = getattr(self.coordinator.data, 'channels', [])
        for ch in channels:
            if ch.number == self._channel_number:
                return ch
        return None

    @property
    def native_value(self):
        channel = self._get_channel()
        return getattr(channel, self._field["key"], None) if channel else None

    async def async_set_native_value(self, value):
        import logging
        _LOGGER = logging.getLogger(__name__)
        channel = self._get_channel()
        if not channel:
            _LOGGER.error(f"[WLANThermo] ChannelNumber: Channel {self._channel_number} not found for set_native_value")
            return
        _LOGGER.warning(f"[WLANThermo] ChannelNumber: Setting {self._field['key']} for channel {channel.number} to {value}")
        api = self.coordinator.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        channel_data = {
            "number": channel.number,
            "name": channel.name,
            "typ": channel.typ,
            "min": value if self._field["key"] == "min" else channel.min,
            "max": value if self._field["key"] == "max" else channel.max,
            "alarm": channel.alarm,
            "color": channel.color,
        }
        _LOGGER.warning(f"[WLANThermo] ChannelNumber: Sending to API: {channel_data}")
        result = await api.async_set_channel(channel_data)
        _LOGGER.warning(f"[WLANThermo] ChannelNumber: API result: {result}")
        await self.coordinator.async_request_refresh()

class WlanthermoPitmasterNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, pitmaster, field):
        super().__init__(coordinator)
        self._pitmaster_id = pitmaster.id
        self._field = field
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo_BBQ")
            else:
                device_name = "WLANThermo_BBQ"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Pitmaster {pitmaster.id} {field['name']}"
        self._attr_unique_id = f"{safe_device_name}_pitmaster_{pitmaster.id}_{field['key']}"
        self.entity_id = f"number.{safe_device_name}_pitmaster_{pitmaster.id}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_native_min_value = field["min"]
        self._attr_native_max_value = field["max"]
        self._attr_native_step = field["step"]
        self._attr_native_unit_of_measurement = field["unit"]
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id if hasattr(self.coordinator, 'config_entry') else None
        hass = getattr(self.coordinator, 'hass', None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    def _get_pitmaster(self):
        pitmasters = getattr(self.coordinator.data, 'pitmasters', [])
        for pm in pitmasters:
            if pm.id == self._pitmaster_id:
                return pm
        return None

    @property
    def native_value(self):
        pitmaster = self._get_pitmaster()
        return getattr(pitmaster, self._field["key"], None) if pitmaster else None

    async def async_set_native_value(self, value):
        import logging
        _LOGGER = logging.getLogger(__name__)
        pitmaster = self._get_pitmaster()
        if not pitmaster:
            _LOGGER.error(f"[WLANThermo] PitmasterNumber: Pitmaster {self._pitmaster_id} not found for set_native_value")
            return
        _LOGGER.warning(f"[WLANThermo] PitmasterNumber: Setting {self._field['key']} for pitmaster {pitmaster.id} to {value}")
        api = self.coordinator.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        pitmaster_data = {
            "id": pitmaster.id,
            "channel": pitmaster.channel,
            "pid": pitmaster.pid,
            "value": value if self._field["key"] == "value" else pitmaster.value,
            "set": value if self._field["key"] == "set" else pitmaster.set,
            "typ": pitmaster.typ,
        }
        _LOGGER.warning(f"[WLANThermo] PitmasterNumber: Sending to API: {pitmaster_data}")
        result = await api.async_set_pitmaster(pitmaster_data)
        _LOGGER.warning(f"[WLANThermo] PitmasterNumber: API result: {result}")
        await self.coordinator.async_request_refresh()
