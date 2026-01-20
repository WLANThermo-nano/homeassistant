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
    entry_id = config_entry.entry_id
    entry_data = hass.data[DOMAIN][entry_id]
    coordinator = entry_data["coordinator"]

    entity_store = entry_data.setdefault("entities", {})
    entity_store.setdefault("lights", set())

    async def _async_discover_lights():
        if not coordinator.data:
            return

    entities = []
    for channel in coordinator.data.channels:
        entities.append(
            WlanthermoChannelColorText(coordinator, channel, entry_data)
        )
        entities.append(
            WlanthermoChannelNameText(coordinator, channel, entry_data)
        )

    async_add_entities(entities)


class WlanthermoChannelColorText(CoordinatorEntity, TextEntity):
    """
    Text entity for displaying the color of a channel as a hex string (read-only).
    """
    def __init__(self, coordinator, channel, entry_data):
        super().__init__(coordinator)

        self._channel_number = channel.number
        self._attr_has_entity_name = True
        self._attr_translation_key = "channel_color"
        self._attr_translation_placeholders = {
            "channel_number": str(channel.number)
        }
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_"
            f"channel_{channel.number}_color"
        )
        self._attr_icon = "mdi:palette"
        self._attr_pattern = HEX_PATTERN
        self._attr_min_length = 7
        self._attr_max_length = 7
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_read_only = True
        self._attr_device_info = entry_data["device_info"]

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        for ch in getattr(self.coordinator.data, "channels", []):
            if ch.number == self._channel_number:
                return ch
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
    def __init__(self, coordinator, channel, entry_data):
        super().__init__(coordinator)

        self._channel_number = channel.number

        self._attr_has_entity_name = True
        self._attr_translation_key = "channel_name"
        self._attr_translation_placeholders = {
            "channel_number": str(channel.number)
        }
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_"
            f"channel_{channel.number}_name"
        )
        self._attr_icon = "mdi:rename-box"
        self._attr_max_length = 10
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_device_info = entry_data["device_info"]

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        for ch in getattr(self.coordinator.data, "channels", []):
            if ch.number == self._channel_number:
                return ch
        return None

    @property
    def native_value(self):
        """
        Return the current name of the channel.
        """
        channel = self._get_channel()
        return channel.name if channel else None

    async def async_set_value(self, value: str):
        """
        Set a new name for the channel and update the device via the API.
        """
        api = self.coordinator.hass.data[DOMAIN][
            self.coordinator.config_entry.entry_id
        ]["api"]

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
