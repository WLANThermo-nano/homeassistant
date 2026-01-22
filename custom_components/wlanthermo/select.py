"""
Select platform for WLANThermo adjustable values.
Exposes probe type, alarm mode, pitmaster state, PID profile, and channel as Home Assistant select entities.
"""

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
import logging
_LOGGER = logging.getLogger(__name__)

ALARM_OPTIONS = ["off", "push", "buzzer", "push_buzzer"]

PITMASTER_SELECT_FIELDS = [
    {
        "key": "typ",
        "icon": "mdi:state-machine",
        "options": [],
    },
    {
        "key": "pid",
        "icon": "mdi:chart-bell-curve",
        "options": [],
    },
]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up select entities for each channel and pitmaster in the config entry.
    Populates options from translations and device settings.
    """
    entry_id = config_entry.entry_id
    entry_data = hass.data[DOMAIN][entry_id]

    coordinator = entry_data["coordinator"]

    # Device offline? → coordinator.data = None → Plattformen NICHT laden
    if coordinator.data is None:
        return

    entities = []

    settings = getattr(hass.data[DOMAIN][config_entry.entry_id]["api"], 'settings', None)
    sensor_types = []
    sensor_type_map = {}

    if settings and hasattr(settings, 'sensors'):
        try:
            for idx, s in enumerate(settings.sensors):
                name = getattr(s, 'name', f"Typ {idx}")
                sensor_types.append(name)
                sensor_type_map[name] = idx
        except Exception as e:
            _LOGGER.error(f"WLANThermo: Failed to extract sensor type names as objects: {e}. Trying dict fallback.")
            for i, s in enumerate(settings.sensors):
                name = s.get('name', f"Typ {i}")
                sensor_types.append(name)
                sensor_type_map[name] = i

    if not sensor_types:
        _LOGGER.error("WLANThermo: No sensor types found in settings.sensors. Using fallback types.")
        sensor_types = ["Typ 0", "Typ 1", "Typ 2"]
        sensor_type_map = {name: i for i, name in enumerate(sensor_types)}

    # Add select entities for each channel
    for channel in coordinator.data.channels:
        entities.append(WlanthermoChannelSelect(coordinator, channel, {
            "key": "alarm",
            "icon": "mdi:alarm",
            "options": ALARM_OPTIONS,
        }, entry_data))

        if not getattr(channel, "fixed", False):
            entities.append(WlanthermoChannelSelect(coordinator, channel, {
                "key": "typ",
                "name": "Probe Type",
                "icon": "mdi:thermometer",
                "options": sensor_types,
                "sensor_type_map": sensor_type_map,
            }, entry_data))

    # Prepare PID profile and pitmaster type options for pitmasters
    pid_profiles = []
    pid_profile_names = []
    pitmaster_type_options: list[str] = []


    if settings and hasattr(settings, 'pid'):
        pid_profiles = settings.pid
        pid_profile_names = [p.name for p in pid_profiles]

    if not pid_profile_names:
        pid_profile_names = ["Profile 0", "Profile 1", "Profile 2"]


    if coordinator.data and hasattr(coordinator.data, "pitmaster_types"):
        pitmaster_type_options = coordinator.data.pitmaster_types.options

    if not pitmaster_type_options:
        pitmaster_type_options = ["off"]


    # Add select entities for each pitmaster
    for pitmaster in coordinator.data.pitmasters:
        channels = getattr(coordinator.data, 'channels', [])
        filtered_channels = [ch for ch in channels if not getattr(ch, 'connected', False)]
        channel_options = [ch.name for ch in filtered_channels]
        channel_number_by_name = {ch.name: ch.number for ch in filtered_channels}
        channel_name_map = {ch.number: ch.name for ch in filtered_channels}

        entities.append(WlanthermoPitmasterSelect(
            coordinator,
            pitmaster,
            {
                "key": "channel",
                "name": "Channel",
                "icon": "mdi:link-variant",
                "options": channel_options,
            },
            entry_data,
            channel_options=channel_options,
            channel_number_by_name=channel_number_by_name,
            channel_name_map=channel_name_map
        ))

        for field in PITMASTER_SELECT_FIELDS:
            field = field.copy()

            if field["key"] == "typ":
                field["options"] = pitmaster_type_options


                entities.append(
                    WlanthermoPitmasterSelect(
                        coordinator, pitmaster, field, entry_data
                    )
                )

            elif field["key"] == "pid":
                field["options"] = pid_profile_names
                entities.append(
                    WlanthermoPitmasterSelect(
                        coordinator,
                        pitmaster,
                        field,
                        entry_data,
                        pid_profiles=pid_profiles,
                    )
                )

    async_add_entities(entities)

class WlanthermoChannelSelect(CoordinatorEntity, SelectEntity):
    """
    Select entity for a channel's probe type or alarm mode.
    Allows user to select probe type or alarm mode for each channel.
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
        self._attr_options = field["options"]
        self._attr_device_info = entry_data["device_info"]

        self._probe_type_key = field.get("key") == "typ"
        self._fixed = getattr(channel, "fixed", False)
        self._attr_disabled = self._probe_type_key and self._fixed

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        channels = getattr(self.coordinator.data, 'channels', [])
        for ch in channels:
            if ch.number == self._channel_number:
                return ch
        return None

    async def async_select_option(self, option):
        """
        Handle user selecting an option for this channel field.
        Updates the channel via the API and refreshes coordinator data.
        """
        api = self.coordinator.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        channel = self._get_channel()
        if not channel:
            _LOGGER.error(f"[WLANThermo] ChannelSelect: Channel {self._channel_number} not found for select_option")
            return

        value = option
        if self._field["key"] == "alarm":
            value = self._attr_options.index(option)

        channel_data = {
            "number": channel.number,
            "name": channel.name,
            "typ": value if self._field["key"] == "typ" else channel.typ,
            "temp": channel.temp,
            "min": channel.min,
            "max": channel.max,
            "alarm": value if self._field["key"] == "alarm" else channel.alarm,
            "color": channel.color,
        }

        await api.async_set_channel(channel_data)
        await self.coordinator.async_request_refresh()

    @property
    def current_option(self):
        """
        Return the currently selected option for this channel field.
        """
        channel = self._get_channel()
        if not channel:
            return None
        if self._field["key"] == "alarm":
            alarm_value = getattr(channel, "alarm", None)
            options = self._attr_options
            if options and alarm_value is not None and 0 <= alarm_value < len(options):
                return options[alarm_value]

        if self._field["key"] == "typ":
            typ_value = getattr(channel, "typ", None)
            options = self._attr_options
            if options and typ_value is not None and 0 <= typ_value < len(options):
                return options[typ_value]
            return None

        return getattr(channel, self._field["key"], None)

class WlanthermoPitmasterSelect(CoordinatorEntity, SelectEntity):
    """
    Select entity for a pitmaster's state, PID profile, or channel.
    Allows user to select pitmaster state, PID profile, or channel for each pitmaster.
    """
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        pitmaster,
        field,
        entry_data,
        *,
        pid_profiles=None,
        channel_options=None,
        channel_number_by_name=None,
        channel_name_map=None,
    ):
        super().__init__(coordinator)

        self._pitmaster_id = pitmaster.id
        self._field = field

        self._pid_profiles = pid_profiles or []
        self._channel_options = channel_options or []
        self._channel_number_by_name = channel_number_by_name or {}
        self._channel_name_map = channel_name_map or {}

        self._attr_translation_key = f"pitmaster_{field['key']}"
        self._attr_translation_placeholders = {
            "pitmaster_number": str(pitmaster.id + 1)
        }

        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_"
            f"pitmaster_{pitmaster.id}_{field['key']}"
        )

        self._attr_icon = field["icon"]
        self._attr_options = field["options"]
        self._attr_device_info = entry_data["device_info"]

    def _get_pitmaster(self):
        """
        Helper to get the current pitmaster object from the coordinator data.
        """
        for pm in getattr(self.coordinator.data, "pitmasters", []):
            if pm.id == self._pitmaster_id:
                return pm
        return None

    @property
    def current_option(self):
        pitmaster = self._get_pitmaster()
        if not pitmaster:
            return None

        if self._field["key"] == "typ" and pitmaster.typ in self._attr_options:
            return pitmaster.typ

        if self._field["key"] == "pid":
            for p in self._pid_profiles:
                if p.id == pitmaster.pid:
                    return p.name

        if self._field["key"] == "channel":
            for ch in getattr(self.coordinator.data, "channels", []):
                if ch.number == pitmaster.channel:
                    return ch.name
        return None

    async def async_select_option(self, option: str):
        """
        Handle user selecting an option for this pitmaster field.
        Updates the pitmaster via the API and refreshes coordinator data.
        """
        pitmaster = self._get_pitmaster()
        if not pitmaster:
            return

        api = self.coordinator.hass.data[DOMAIN][
            self.coordinator.config_entry.entry_id
        ]["api"]

        data = {
            "id": pitmaster.id,
            "channel": pitmaster.channel,
            "pid": pitmaster.pid,
            "value": pitmaster.value,
            "set": pitmaster.set,
            "typ": pitmaster.typ,
        }

        if self._field["key"] == "typ":
            data["typ"] = option

        elif self._field["key"] == "pid":
            for p in self._pid_profiles:
                if p.name == option:
                    data["pid"] = p.id
                    break

        elif self._field["key"] == "channel":
            for ch in getattr(self.coordinator.data, "channels", []):
                if ch.name == option:
                    data["channel"] = ch.number
                    break

        await api.async_set_pitmaster(data)
        await self.coordinator.async_request_refresh()

