"""
Switch platform for WLANThermo PID profile fields (opl).
"""
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up switch entities for each PID profile (OPL).
    """
    entry_id = config_entry.entry_id
    entry_data = hass.data[DOMAIN][entry_id]
    coordinator = entry_data["coordinator"]

    entity_store = entry_data.setdefault("entities", {})
    entity_store.setdefault("pidprofile_switch", set())

    async def _async_discover_entities():
        if not coordinator.data:
            return

        new_entities = []

        for profile in getattr(coordinator.api.settings, "pid", []):
            unique_key = f"{profile.id}_opl"
            if unique_key not in entity_store["pidprofile_switch"]:
                new_entities.append(
                    WlanthermoPidProfileOplSwitch(coordinator,entry_data,profile_id=profile.id)
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


    def __init__(self, coordinator, entry_data, *, profile_id: int):
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
        for profile in getattr(self.coordinator.api.settings, "pid", []):
            if profile.id == self._profile_id:
                return bool(profile.opl)
        return False

    async def async_turn_on(self, **kwargs):
        await self._async_set_opl(True)

    async def async_turn_off(self, **kwargs):
        await self._async_set_opl(False)

    async def _async_set_opl(self, value: bool):
        payload = {
            "id": self._profile_id,
            "opl": value,
        }

        success = await self.coordinator.api.async_set_pid(
            [payload],
            method="PATCH",
        )

        if success:
            await self.coordinator.async_request_refresh()
