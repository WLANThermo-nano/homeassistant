
"""
Text platform for WLANThermo.
Provides Home Assistant text entities for adjustable channel name and color.
Allows users to view and (for name) set channel names and view channel color as hex.
"""


from typing import Any, Callable
from homeassistant.components.text import TextEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

HEX_PATTERN = r"^#[0-9A-Fa-f]{6}$"

async def async_setup_entry(hass: Any, config_entry: Any, async_add_entities: Callable) -> None:
    """
    Set up text entities for each channel (color and name) for WLANThermo.

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
    entity_store.setdefault("text_channels", set())
    entity_store.setdefault("text_pidprofiles", set())

    async def _async_discover_entities() -> None:
        """
        Discover and add new text entities for each channel and PID profile.
        Returns:
            None.
        """
        if not coordinator.data:
            return
        new_entities = []
        for channel in getattr(coordinator.data, "channels", []):
            ch_id = channel.number
            if ch_id not in entity_store["text_channels"]:
                new_entities.append(
                    WlanthermoChannelNameText(coordinator, channel, entry_data)
                )
                entity_store["text_channels"].add(ch_id)
        for profile in getattr(coordinator.api.settings, "pid", []):
            pid_id = profile.id
            if pid_id not in entity_store["text_pidprofiles"]:
                new_entities.append(
                    WlanthermoPidProfileNameText(
                        coordinator,
                        entry_data,
                        profile_id=pid_id,
                    )
                )
                entity_store["text_pidprofiles"].add(pid_id)
        if new_entities:
            async_add_entities(new_entities)
    coordinator.async_add_listener(_async_discover_entities)
    await _async_discover_entities()


class WlanthermoChannelNameText(CoordinatorEntity, TextEntity):
    """
    Text entity for displaying and setting the name of a channel.
    """
    def __init__(self, coordinator: Any, channel: Any, entry_data: dict) -> None:
        """
        Initialize a WlanthermoChannelNameText entity.
        Args:
            coordinator: Data update coordinator.
            channel: Channel object.
            entry_data: Dictionary with entry data.
        Returns:
            None.
        """
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
    def native_value(self) -> str | None:
        """
        Return the current name of the channel.
        Returns:
            The channel name, or None if unavailable.
        """
        channel = self._get_channel()
        return channel.name if channel else None

    async def async_set_value(self, value: str) -> None:
        """
        Set a new name for the channel and update the device via the API.
        Args:
            value: The new channel name.
        Returns:
            None.
        """
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
        await self.coordinator.api.async_set_channel(channel_data)
        await self.coordinator.async_request_refresh()


class WlanthermoPidProfileNameText(CoordinatorEntity, TextEntity):
    """
    Text entity for PID profile name.
    """
    _attr_has_entity_name = True
    _attr_icon = "mdi:form-textbox"
    _attr_native_min = 0
    _attr_native_max = 14   # API: max 14 chars
    _attr_pattern = r".*"   # UTF-8 allowed

    def __init__(self, coordinator: Any, entry_data: dict, *, profile_id: int) -> None:
        """
        Initialize a WlanthermoPidProfileNameText entity.
        Args:
            coordinator: Data update coordinator.
            entry_data: Dictionary with entry data.
            profile_id: PID profile ID.
        Returns:
            None.
        """
        super().__init__(coordinator)
        self._profile_id = profile_id
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_pid_{profile_id}_name"
        )
        self._attr_device_info = entry_data["device_info"]
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_translation_key = "pidprofile_name"
        self._attr_translation_placeholders = {
            "profile_id": str(profile_id)
        }

    @property
    def native_value(self) -> str | None:
        """
        Return the current name of the PID profile.
        Returns:
            The profile name, or None if unavailable.
        """
        for profile in getattr(self.coordinator.api.settings, "pid", []):
            if profile.id == self._profile_id:
                return profile.name
        return None

    async def async_set_value(self, value: str) -> None:
        """
        Set a new name for the PID profile and update the device via the API.
        Args:
            value: The new profile name.
        Returns:
            None.
        """
        for p in self.coordinator.api.settings.pid:
            if p.id == self._profile_id:
                setattr(p, self._field, value)
                payload = p.to_full_payload()
                success = await self.coordinator.api.async_set_pid_profile(
                    [payload],
                )
                if success:
                    await self.coordinator.async_request_refresh()
                return
