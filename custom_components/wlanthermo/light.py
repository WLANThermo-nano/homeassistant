
from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
from .const import DOMAIN

class WlanthermoChannelColorLight(CoordinatorEntity, LightEntity):
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, channel):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._channel_number = channel.number

        device_name = getattr(coordinator, "device_name", None)
        if not device_name:
            entry_id = getattr(coordinator, "config_entry", None).entry_id \
                if hasattr(coordinator, "config_entry") else None
            hass = getattr(coordinator, "hass", None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get(
                    "name", "WLANThermo_BBQ"
                )
            else:
                device_name = "WLANThermo_BBQ"

        safe_device_name = device_name.replace(" ", "_").lower()

        self._attr_name = f"{device_name} Channel {channel.number} Color"
        self._attr_unique_id = f"{safe_device_name}_channel_{channel.number}_color"
        self._attr_icon = "mdi:palette"
        self._attr_color_mode = ColorMode.RGB

    def _get_channel(self):
        for ch in getattr(self._coordinator.data, "channels", []):
            if ch.number == self._channel_number:
                return ch
        return None
        
    @property
    def available(self):
        return self._get_channel() is not None

    @property
    def device_info(self):
        entry_id = self.coordinator.config_entry.entry_id \
            if hasattr(self.coordinator, "config_entry") else None
        hass = getattr(self.coordinator, "hass", None)
        if hass and entry_id:
            return hass.data[DOMAIN][entry_id]["device_info"]
        return None

    @property
    def is_on(self):
        return True

    @property
    def rgb_color(self):
        channel = self._get_channel()
        hex_color = getattr(channel, "color", "#000000") if channel else "#000000"
        hex_color = hex_color.lstrip("#")
        try:
            return (
                int(hex_color[0:2], 16),
                int(hex_color[2:4], 16),
                int(hex_color[4:6], 16),
            )
        except Exception:
            return (0, 0, 0)

    async def async_turn_on(self, **kwargs):
        api = self.coordinator.hass.data[DOMAIN][
            self.coordinator.config_entry.entry_id
        ]["api"]

        channel = self._get_channel()
        if not channel:
            return

        if "rgb_color" in kwargs:
            r, g, b = kwargs["rgb_color"]
            hex_value = f"#{r:02X}{g:02X}{b:02X}"
        else:
            hex_value = getattr(channel, "color", "#000000")

        channel_data = {
            "number": channel.number,
            "name": channel.name,
            "typ": channel.typ,
            "min": channel.min,
            "max": channel.max,
            "alarm": channel.alarm,
            "color": hex_value,
        }

        await api.async_set_channel(channel_data)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        return


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities = []
    for channel in coordinator.data.channels:
        entities.append(WlanthermoChannelColorLight(coordinator, channel))
    async_add_entities(entities)
