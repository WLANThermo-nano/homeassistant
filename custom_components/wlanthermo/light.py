"""
Light platform for WLANThermo integration.
Exposes each channel's color as a Home Assistant light entity.
"""

from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory

from typing import Any
from .const import DOMAIN



async def async_setup_entry(hass: Any, config_entry: Any, async_add_entities: Any) -> None:
    """
    Set up light entities for each channel in the config entry.
    Args:
        hass: Home Assistant instance.
        config_entry: Config entry for the integration.
        async_add_entities: Callback to add entities.
    Returns:
        None.
    """
    entry_id = config_entry.entry_id
    entry_data = hass.data[DOMAIN][entry_id]
    coordinator = entry_data["coordinator"]
    entity_store = entry_data.setdefault("entities", {})
    entity_store.setdefault("lights", set())

    async def _async_discover_lights() -> None:
        """
        Discover and add new light entities for each channel.
        Returns:
            None.
        """
        if not coordinator.data:
            return
        new_entities = []
        for channel in getattr(coordinator.data, "channels", []):
            ch_id = channel.number
            if ch_id not in entity_store["lights"]:
                new_entities.append(
                    WlanthermoChannelColorLight(coordinator, channel, entry_data)
                )
                entity_store["lights"].add(ch_id)
        if new_entities:
            async_add_entities(new_entities)

    await _async_discover_lights()
    coordinator.async_add_listener(_async_discover_lights)


class WlanthermoChannelColorLight(CoordinatorEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB
    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True
    _attr_icon = "mdi:palette"

    def __init__(self, coordinator: Any, channel: Any, entry_data: dict) -> None:
        """
        Initialize a WlanthermoChannelColorLight entity.
        Args:
            coordinator: Data update coordinator.
            channel: Channel object.
            entry_data: Dictionary with entry data.
        Returns:
            None.
        """
        super().__init__(coordinator)
        self._channel_number = channel.number
        self._attr_translation_key = "channel_color"
        self._attr_translation_placeholders = {
            "channel_number": str(channel.number)
        }
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_channel_{channel.number}_color_rgb"
        )
        self._attr_device_info = entry_data["device_info"]

    def _get_channel(self) -> Any:
        """
        Helper to get the current channel object from the coordinator data.
        Returns:
            Channel object or None if not found.
        """
        for ch in getattr(self.coordinator.data, "channels", []):
            if ch.number == self._channel_number:
                return ch
        return None

    @property
    def available(self) -> bool:
        """
        Entity is available if the channel exists in the latest data.
        Returns:
            True if available, False otherwise.
        """
        return (
            self.coordinator.last_update_success
            and self._get_channel() is not None
        )

    @property
    def is_on(self) -> bool:
        """
        The color light is always considered on (virtual entity).
        Returns:
            Always True.
        """
        return True

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """
        Return the current color of the channel as an RGB tuple.
        Returns:
            Tuple of (R, G, B) values.
        """
        channel = self._get_channel()
        hex_color = getattr(channel, "color", "#000000") if channel else "#000000"
        hex_color = hex_color.lstrip("#")
        try:
            # Convert hex color string to RGB tuple.
            return (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16),
            )
        except Exception:
            return (0, 0, 0)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Handle turning on the light (set channel color).
        Updates the channel color via the API and refreshes coordinator data.
        Args:
            **kwargs: Keyword arguments, may include 'rgb_color'.
        Returns:
            None.
        """
        channel = self._get_channel()
        if not channel:
            return
        # Convert RGB tuple to hex string.
        if "rgb_color" in kwargs:
            r, g, b = kwargs["rgb_color"]
            color = f"#{r:02X}{g:02X}{b:02X}"
        else:
            color = channel.color
        payload = {
            "number": channel.number,
            "name": channel.name,
            "typ": channel.typ,
            "temp": channel.temp,
            "min": channel.min,
            "max": channel.max,
            "alarm": channel.alarm,
            "color": color,
        }
        result = await self.coordinator.api.async_set_channel(payload)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Turning off the color light is a no-op (virtual entity).
        Args:
            **kwargs: Keyword arguments (unused).
        Returns:
            None.
        """
        return
