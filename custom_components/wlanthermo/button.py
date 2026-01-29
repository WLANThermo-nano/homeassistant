"""
Button platform for WLANThermo PID profile fields (opl).
"""
from typing import Any, Callable
from homeassistant.helpers.entity import EntityCategory
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import time
import logging
_LOGGER = logging.getLogger(__name__)

DEBOUNCE_SECONDS = 5


async def async_setup_entry(
    hass: Any,
    config_entry: Any,
    async_add_entities: Callable,
) -> None:
    """
    Set up button entities for WLANThermo.
    """
    entry_id = config_entry.entry_id
    entry_data = hass.data[DOMAIN][entry_id]
    coordinator = entry_data["coordinator"]

    entity_store = entry_data.setdefault("entities", {})
    entity_store.setdefault("buttons", set())

    async def _async_discover_entities() -> None:
        """
        Discover and add button entities.
        """
        if not coordinator.data:
            return

        new_entities = []

                # Telegram test button
        key = "telegram_test"
        if key not in entity_store["buttons"]:
            new_entities.append(
                WlanthermoTelegramTestButton(
                    coordinator,
                    entry_data,
                )
            )
            entity_store["buttons"].add(key)

        # Pushover test button
        key = "pushover_test"
        if key not in entity_store["buttons"]:
            new_entities.append(
                WlanthermoPushoverTestButton(
                    coordinator,
                    entry_data,
                )
            )
            entity_store["buttons"].add(key)


        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(_async_discover_entities)
    await _async_discover_entities()


class WlanthermoTelegramTestButton(CoordinatorEntity, ButtonEntity):
    """
    Button to send a test Telegram message.
    """
    _attr_has_entity_name = True
    _attr_icon = "mdi:message-alert"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "telegram_test"

    def __init__(self, coordinator, entry_data: dict) -> None:
        super().__init__(coordinator)
        self._last_press: float = 0.0
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_telegram_test"
        )
        self._attr_device_info = entry_data["device_info"]

    async def async_press(self) -> None:
        now = time.monotonic()
        if now - self._last_press < DEBOUNCE_SECONDS:
            return
        self._last_press = now
        telegram = self.coordinator.data.push.telegram
        payload = {
            "test": True,
            "telegram": telegram.to_payload(),
        }
        await self.coordinator.api.async_set_push(payload)

    @property
    def available(self) -> bool:
        data = self.coordinator.data
        if not data or not data.push:
            return False

        telegram = data.push.telegram
        return (
            bool(telegram.token)
            and bool(telegram.chat_id)
        )


class WlanthermoPushoverTestButton(CoordinatorEntity, ButtonEntity):
    """
    Button to send a test Pushover message.
    """
    _attr_has_entity_name = True
    _attr_icon = "mdi:bell-ring"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_translation_key = "pushover_test"

    def __init__(self, coordinator, entry_data: dict) -> None:
        super().__init__(coordinator)
        self._last_press: float = 0.0
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_pushover_test"
        )
        self._attr_device_info = entry_data["device_info"]

    async def async_press(self) -> None:
        now = time.monotonic()
        if now - self._last_press < DEBOUNCE_SECONDS:
            return
        self._last_press = now
        pushover = self.coordinator.data.push.pushover
        payload = {
            "test": True,
            "pushover": pushover.to_payload(),
        }
        await self.coordinator.api.async_set_push(payload)

    @property
    def available(self) -> bool:
        data = self.coordinator.data
        if not data or not data.push:
            return False
        pushover = data.push.pushover
        return (
            bool(pushover.token)
            and bool(pushover.user_key)
        )
