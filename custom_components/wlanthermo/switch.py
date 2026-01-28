"""
Switch platform for WLANThermo PID profile fields (opl).
"""
from typing import Any, Callable
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass: Any, config_entry: Any, async_add_entities: Callable) -> None:
    """
    Set up switch entities for each PID profile (OPL).

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
    entity_store.setdefault("pidprofile_switch", set())

    async def _async_discover_entities() -> None:
        """
        Discover and add new switch entities for each PID profile.
        Returns:
            None.
        """
        if not coordinator.data:
            return
        new_entities = []
        for profile in getattr(coordinator.api.settings, "pid", []):
            for key, cls in (
                ("opl", WlanthermoPidProfileOplSwitch),
                ("link", WlanthermoPidProfileLinkSwitch),
            ):
                unique_key = f"{profile.id}_{key}"
                if unique_key not in entity_store["pidprofile_switch"]:
                    new_entities.append(
                        cls(
                            coordinator,
                            entry_data,
                            profile_id=profile.id,
                        )
                    )
                    entity_store["pidprofile_switch"].add(unique_key)
        if new_entities:
            async_add_entities(new_entities)
    coordinator.async_add_listener(_async_discover_entities)
    await _async_discover_entities()


class WlanthermoPidProfileOplSwitch(CoordinatorEntity, SwitchEntity):
    """
    Switch entity for PID profile open lid detection (opl).
    """
    _attr_has_entity_name = True
    _attr_icon = "mdi:pot-steam"
    _attr_entity_category = EntityCategory.CONFIG


    def __init__(self, coordinator: Any, entry_data: dict, *, profile_id: int) -> None:
        """
        Initialize a WlanthermoPidProfileOplSwitch entity.
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
            f"{coordinator.config_entry.entry_id}_pid_{profile_id}_opl"
        )
        self._attr_device_info = entry_data["device_info"]
        self._attr_translation_key = "pidprofile_opl"
        self._attr_translation_placeholders = {
            "profile_id": str(profile_id)
        }

    @property
    def is_on(self) -> bool:
        """
        Return True if open lid detection is enabled for this PID profile.
        Returns:
            True if enabled, False otherwise.
        """
        for profile in getattr(self.coordinator.api.settings, "pid", []):
            if profile.id == self._profile_id:
                return bool(profile.opl)
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """
        Turn on open lid detection for this PID profile.
        Args:
            **kwargs: Additional arguments.
        Returns:
            None.
        """
        await self._async_set_opl(True)

    async def async_turn_off(self, **kwargs) -> None:
        """
        Turn off open lid detection for this PID profile.
        Args:
            **kwargs: Additional arguments.
        Returns:
            None.
        """
        await self._async_set_opl(False)

    async def _async_set_opl(self, value: bool) -> None:
        """
        Set the open lid detection value for this PID profile and update the coordinator.
        Args:
            value: True to enable, False to disable.
        Returns:
            None.
        """
        for p in self.coordinator.api.settings.pid:
            if p.id == self._profile_id:
                p.opl = value
                payload = p.to_full_payload()
                success = await self.coordinator.api.async_set_pid_profile(
                    [payload],
                )
                if success:
                    await self.coordinator.async_request_refresh()
                return
            

class WlanthermoPidProfileLinkSwitch(CoordinatorEntity, SwitchEntity):
    """
    Switch entity for PID profile actuator link (DAMPER only).
    """
    _attr_has_entity_name = True
    _attr_icon = "mdi:link-variant"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: Any, entry_data: dict, *, profile_id: int) -> None:
        """
        Initialize a WlanthermoPidProfileLinkSwitch entity.
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
            f"{coordinator.config_entry.entry_id}_pid_{profile_id}_link"
        )
        self._attr_device_info = entry_data["device_info"]
        self._attr_translation_key = "pidprofile_link"
        self._attr_translation_placeholders = {
            "profile_id": str(profile_id)
        }

    @property
    def is_on(self) -> bool:
        """
        Return True if actuator link is enabled for this PID profile.
        Returns:
            True if enabled, False otherwise.
        """
        for p in self.coordinator.api.settings.pid:
            if p.id == self._profile_id:
                return bool(p.link)
        return False

    @property
    def available(self) -> bool:
        """
        Return True if this PID profile supports actuator link.
        Returns:
            True if supported, False otherwise.
        """
        for p in self.coordinator.api.settings.pid:
            if p.id == self._profile_id:
                return p.supports_link
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """
        Turn on actuator link for this PID profile.
        Args:
            **kwargs: Additional arguments.
        Returns:
            None.
        """
        await self._async_set_link(True)

    async def async_turn_off(self, **kwargs) -> None:
        """
        Turn off actuator link for this PID profile.
        Args:
            **kwargs: Additional arguments.
        Returns:
            None.
        """
        await self._async_set_link(False)

    async def _async_set_link(self, value: bool) -> None:
        """
        Set the actuator link value for this PID profile and update the coordinator.
        Args:
            value: True to enable, False to disable.
        Returns:
            None.
        """
        for p in self.coordinator.api.settings.pid:
            if p.id == self._profile_id:
                p.link = int(value)
                payload = p.to_full_payload()
                success = await self.coordinator.api.async_set_pid_profile(
                    [payload],
                )
                if success:
                    await self.coordinator.async_request_refresh()
                return
