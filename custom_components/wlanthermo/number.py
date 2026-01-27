"""
Number platform for WLANThermo adjustable values.
Exposes min/max temperature and pitmaster values as Home Assistant number entities.
"""

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import EntityCategory
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
ICON_MAP = {
    "jp": "mdi:rocket-launch",
    "DCmmin": "mdi:cosine-wave",
    "DCmmax": "mdi:sine-wave",
    "SPmin": "mdi:axis-arrow",
    "SPmax": "mdi:axis-arrow",
    "link": "mdi:link-variant",
}

async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up number entities for channels, pitmasters and PID profiles.
    """
    entry_id = config_entry.entry_id
    entry_data = hass.data[DOMAIN][entry_id]
    coordinator = entry_data["coordinator"]

    entity_store = entry_data.setdefault("entities", {})
    entity_store.setdefault("channel_numbers", set())
    entity_store.setdefault("pitmaster_numbers", set())
    entity_store.setdefault("pidprofile_numbers", set())

    # field, min, max
    PID_NUMBER_FIELDS = [
        ("jp", 0, 100),
        ("DCmmin", 0, 100),
        ("DCmmax", 0, 100),
        ("SPmin", 0, 3000),
        ("SPmax", 0, 3000),
    ]


    async def _async_discover_numbers():
        if not coordinator.data:
            return

        new_entities: list[NumberEntity] = []

        # ---------- Channels ----------
        for channel in getattr(coordinator.data, "channels", []):
            ch_id = channel.number
            if channel.number not in entity_store["channel_numbers"]:

                for field in CHANNEL_NUMBER_FIELDS:
                    new_entities.append(
                        WlanthermoChannelNumber(coordinator,channel,field,entry_data)
                    )

                entity_store["channel_numbers"].add(channel.number)

        # ---------- Pitmasters ----------
        for pitmaster in getattr(coordinator.data, "pitmasters", []):
            if pitmaster.id not in entity_store["pitmaster_numbers"]:

                for field in PITMASTER_NUMBER_FIELDS:
                    new_entities.append(
                        WlanthermoPitmasterNumber(coordinator,pitmaster,field,entry_data)
                )

            entity_store["pitmaster_numbers"].add(pitmaster.id)

        # ---------- PID Profiles ----------
        for profile in getattr(coordinator.api.settings, "pid", []):
            for field, min_v, max_v in PID_NUMBER_FIELDS:
                key = (profile.id, field)
                if key in entity_store["pidprofile_numbers"]:
                    continue

                new_entities.append(
                    WlanthermoPidProfileNumber(
                        coordinator,
                        entry_data,
                        profile_id=profile.id,
                        field=field,
                        min_value=min_v,
                        max_value=max_v,
                    )
                )
                entity_store["pidprofile_numbers"].add(key)


        if new_entities:
            async_add_entities(new_entities)

    await _async_discover_numbers()
    coordinator.async_add_listener(_async_discover_numbers)


class WlanthermoChannelNumber(CoordinatorEntity, NumberEntity):
    """
    Number entity for a channel's min/max temperature.
    Allows user to set min/max values for each channel.
    """
    def __init__(self, coordinator, channel, field, entry_data):
        super().__init__(coordinator)
        self._channel_number = channel.number
        self._field = field

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

        result = await self.coordinator.api.async_set_channel(channel_data)
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
        pitmaster = self._get_pitmaster()
        if not pitmaster:
            return
        pitmaster_data = {
            "id": pitmaster.id,
            "channel": pitmaster.channel,
            "pid": pitmaster.pid,
            "value": value if self._field["key"] == "value" else pitmaster.value,
            "set": value if self._field["key"] == "set" else pitmaster.set,
            "typ": pitmaster.typ,
        }
        
        result = await self.coordinator.api.async_set_pitmaster(pitmaster_data)
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
    


class WlanthermoPidProfileNumber(CoordinatorEntity, NumberEntity):
    """
    Number entity for editable PID profile fields.
    """
    _attr_has_entity_name = True
    _attr_icon = "mdi:tune-vertical"
    

    def __init__(
        self,
        coordinator,
        entry_data,
        *,
        profile_id: int,
        field: str,
        min_value: int,
        max_value: int,
    ):
        super().__init__(coordinator)

        self._profile_id = profile_id
        self._field = field

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_pid_{profile_id}_{field}"
        )
        self._attr_device_info = entry_data["device_info"]
        self._attr_translation_key = f"pidprofile_{field}"
        self._attr_translation_placeholders = {
            "profile_id": str(self._profile_id),
        }
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_icon = ICON_MAP.get(field, "mdi:numeric")

        self._attr_native_min_value = min_value
        self._attr_native_max_value = max_value
        self._attr_native_step = 1


    @property
    def native_value(self):
        for profile in getattr(self.coordinator.api.settings, "pid", []):
            if profile.id == self._profile_id:
                return getattr(profile, self._field, None)
        return None

    async def async_set_native_value(self, value):
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

    @property
    def available(self) -> bool:
        for p in self.coordinator.api.settings.pid:
            if p.id == self._profile_id:
                return p.supports_field(self._field)
        return False
