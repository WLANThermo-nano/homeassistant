"""
Text platform for WLANThermo.
Provides Home Assistant text entities for adjustable channel name and color.
Allows users to view and (for name) set channel names and view channel color as hex.
"""

from homeassistant.components.text import TextEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

HEX_PATTERN = r"^#[0-9A-Fa-f]{6}$"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up text entities for each channel (color and name) for WLANThermo.
    """
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities = []
    for channel in coordinator.data.channels:
        entities.append(WlanthermoChannelColorText(coordinator, channel))
        entities.append(WlanthermoChannelNameText(coordinator, channel))
    async_add_entities(entities)

class WlanthermoChannelColorText(CoordinatorEntity, TextEntity):
    """
    Text entity for displaying the color of a channel as a hex string (read-only).
    """
    def __init__(self, coordinator, channel):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._channel_number = channel.number
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo")
            else:
                device_name = "WLANThermo"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Channel {channel.number} Color"
        self._attr_unique_id = f"{safe_device_name}_channel_{channel.number}_color"
        self.entity_id = f"text.{safe_device_name}_channel_{channel.number}_color"
        self._attr_icon = "mdi:palette"
        self._attr_pattern = HEX_PATTERN
        self._attr_min_length = 7
        self._attr_max_length = 7
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_read_only = True

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        channels = getattr(self._coordinator.data, 'channels', [])
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
    def native_value(self):
        """
        Return the current color of the channel as a hex string.
        """
        channel = self._get_channel()
        return getattr(channel, "color", "#000000") if channel else "#000000"

class WlanthermoChannelNameText(CoordinatorEntity, TextEntity):
    """
    Text entity for displaying and setting the name of a channel.
    """
    def __init__(self, coordinator, channel):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._channel_number = channel.number
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo")
            else:
                device_name = "WLANThermo"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Channel {channel.number} Name"
        self._attr_unique_id = f"{safe_device_name}_channel_{channel.number}_name"
        self.entity_id = f"text.{safe_device_name}_channel_{channel.number}_name"
        self._attr_icon = "mdi:rename-box"
        self._attr_max_length = 10
        self._attr_entity_category = EntityCategory.CONFIG

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        channels = getattr(self._coordinator.data, 'channels', [])
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
    def native_value(self):
        """
        Return the current name of the channel.
        """
        channel = self._get_channel()
        return channel.name if channel and hasattr(channel, 'name') else f"Channel {self._channel_number}"

    async def async_set_value(self, value: str):
        """
        Set a new name for the channel and update the device via the API.
        """
        api = self.coordinator.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        channel = self._get_channel()
        if not channel:
            return
        channel_data = {
            "number": channel.number,
            "name": value,
            "typ": channel.typ,
            "min": channel.min,
            "max": channel.max,
            "alarm": channel.alarm,
            "color": channel.color,
        }
        await api.async_set_channel(channel_data)
        await self.coordinator.async_request_refresh()
