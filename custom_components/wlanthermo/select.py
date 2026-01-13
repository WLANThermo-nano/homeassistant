"""
Select platform for WLANThermo adjustable values.
Exposes probe type, alarm mode, pitmaster state, PID profile, and channel as Home Assistant select entities.
"""

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

CHANNEL_SELECT_FIELDS = [
    # Defines which channel fields are exposed as select entities
    {
        "key": "typ",
        "name": "Probe Type",
        "icon": "mdi:thermometer",
        # TODO: Populate options from device/settings
        "options": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    },
    {
        "key": "alarm",
        "name": "Alarm Mode",
        "icon": "mdi:alarm",
        "options": [0, 1, 2, 3],
    },
]

PITMASTER_SELECT_FIELDS = [
    # Defines which pitmaster fields are exposed as select entities
    {
        "key": "typ",
        "name": "Pitmaster State",
        "icon": "mdi:state-machine",
        "options": ["off", "manual", "auto"],
    },
    {
        "key": "pid",
        "name": "PID Profile",
        "icon": "mdi:chart-bell-curve",
        # TODO: Populate options from device/settings
        "options": [0, 1, 2, 3, 4, 5],
    },
]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """
    Set up select entities for each channel and pitmaster in the config entry.
    Populates options from translations and device settings.
    """
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    entities = []
    import json
    import os
    import aiofiles
    lang = hass.config.language if hasattr(hass.config, 'language') else 'en'
    translations_path = os.path.join(os.path.dirname(__file__), 'translations', f'{lang}.json')
    if not os.path.exists(translations_path):
        translations_path = os.path.join(os.path.dirname(__file__), 'translations', 'en.json')
    async with aiofiles.open(translations_path, encoding='utf-8') as f:
        translations = json.loads(await f.read())
    alarm_labels_dict = translations.get("alarm", {})
    alarm_mode_map = {
        0: alarm_labels_dict.get("off", "Off"),
        1: alarm_labels_dict.get("push", "Push"),
        2: alarm_labels_dict.get("buzzer", "Buzzer"),
        3: alarm_labels_dict.get("push_buzzer", "Push + Buzzer"),
    }
    alarm_labels = [alarm_mode_map[i] for i in range(4)]

    settings = getattr(hass.data[DOMAIN][config_entry.entry_id]["api"], 'settings', None)
    sensor_types = []
    sensor_type_map = {}
    import logging
    _LOGGER = logging.getLogger(__name__)
    if settings and hasattr(settings, 'sensors'):
        try:
            # settings.sensors is a list of SensorType objects
            for idx, s in enumerate(settings.sensors):
                name = getattr(s, 'name', f"Typ {idx}")
                sensor_types.append(name)
                sensor_type_map[name] = idx
        except Exception as e:
            _LOGGER.error(f"WLANThermo: Failed to extract sensor type names as objects: {e}. Trying dict fallback.")
            # fallback if sensors is a list of dicts
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
            "name": "Alarm Mode",
            "icon": "mdi:alarm",
            "options": alarm_labels,
            "alarm_mode_map": alarm_mode_map,
        }))
        if not getattr(channel, "fixed", False):
            entities.append(WlanthermoChannelSelect(coordinator, channel, {
                "key": "typ",
                "name": "Probe Type",
                "icon": "mdi:thermometer",
                "options": sensor_types,
                "sensor_type_map": sensor_type_map,
            }))
    # Prepare PID profile options for pitmasters
    pid_profiles = []
    pid_profile_names = []
    if settings and hasattr(settings, 'pid'):
        pid_profiles = settings.pid
        pid_profile_names = [p.name for p in pid_profiles]
    if not pid_profile_names:
        pid_profile_names = ["Profile 0", "Profile 1", "Profile 2"]
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
            channel_options=channel_options,
            channel_number_by_name=channel_number_by_name,
            channel_name_map=channel_name_map
        ))

        for field in PITMASTER_SELECT_FIELDS:
            if field["key"] == "pid":
                field = field.copy()
                field["options"] = pid_profile_names
                entities.append(WlanthermoPitmasterSelect(coordinator, pitmaster, field, pid_profiles=pid_profiles))
            else:
                entities.append(WlanthermoPitmasterSelect(coordinator, pitmaster, field))
    async_add_entities(entities)

class WlanthermoChannelSelect(CoordinatorEntity, SelectEntity):
    """
    Select entity for a channel's probe type or alarm mode.
    Allows user to select probe type or alarm mode for each channel.
    """
    def __init__(self, coordinator, channel, field):
        super().__init__(coordinator)
        self._channel_number = channel.number
        self._field = field
        # Try to get a friendly device name from the coordinator or fallback
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo")
            else:
                device_name = "WLANThermo"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Channel {channel.number} {field['name']}"
        self._attr_unique_id = f"{safe_device_name}_channel_{channel.number}_{field['key']}"
        self.entity_id = f"select.{safe_device_name}_channel_{channel.number}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_options = field["options"]
        self._attr_entity_category = EntityCategory.CONFIG
        self._probe_type_key = field.get("key") == "typ"
        self._fixed = getattr(channel, "fixed", False)
        self._attr_disabled = self._probe_type_key and self._fixed

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

    def _get_channel(self):
        """
        Helper to get the current channel object from the coordinator data.
        """
        channels = getattr(self.coordinator.data, 'channels', [])
        for ch in channels:
            if ch.number == self._channel_number:
                return ch
        return None

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
            if self._attr_options and alarm_value is not None and 0 <= alarm_value < len(self._attr_options):
                return self._attr_options[alarm_value]
            return None

        if self._field["key"] == "typ":
            typ_value = getattr(channel, "typ", None)
            options = self._attr_options
            if options and typ_value is not None and 0 <= typ_value < len(options):
                return options[typ_value]
            return None

        return getattr(channel, self._field["key"], None)

    async def async_select_option(self, option):
        """
        Handle user selecting an option for this channel field.
        Updates the channel via the API and refreshes coordinator data.
        """
        api = self.coordinator.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        channel = self._get_channel()
        if not channel:
            import logging
            logging.getLogger(__name__).error(f"[WLANThermo] ChannelSelect: Channel {self._channel_number} not found for select_option")
            return

        value = option
        if self._field["key"] == "alarm":
            alarm_mode_map = self._field.get("alarm_mode_map", {})
            for k, v in alarm_mode_map.items():
                if v == option:
                    value = k
                    break
        elif self._field["key"] == "typ":
            sensor_type_map = self._field.get("sensor_type_map", {})
            if option in sensor_type_map:
                value = sensor_type_map[option]
            else:
                if option in self._attr_options:
                    value = self._attr_options.index(option)

        channel_data = {
            "number": channel.number,
            "name": channel.name,
            "typ": value if self._field["key"] == "typ" else channel.typ,
            "min": channel.min,
            "max": channel.max,
            "alarm": value if self._field["key"] == "alarm" else channel.alarm,
            "color": channel.color,
        }
        await api.async_set_channel(channel_data)
        await self.coordinator.async_request_refresh()

class WlanthermoPitmasterSelect(CoordinatorEntity, SelectEntity):
    """
    Select entity for a pitmaster's state, PID profile, or channel.
    Allows user to select pitmaster state, PID profile, or channel for each pitmaster.
    """
    def __init__(self, coordinator, pitmaster, field, pid_profiles=None, channel_options=None, channel_number_by_name=None, channel_name_map=None):
        super().__init__(coordinator)
        self._pitmaster_id = pitmaster.id
        self._field = field
        # Try to get a friendly device name from the coordinator or fallback
        device_name = getattr(coordinator, 'device_name', None)
        if not device_name:
            entry_id = getattr(coordinator, 'config_entry', None).entry_id if hasattr(coordinator, 'config_entry') else None
            hass = getattr(coordinator, 'hass', None)
            if hass and entry_id:
                device_name = hass.data[DOMAIN][entry_id]["device_info"].get("name", "WLANThermo")
            else:
                device_name = "WLANThermo"
        safe_device_name = device_name.replace(" ", "_").lower()
        self._attr_name = f"{device_name} Pitmaster {pitmaster.id + 1} {field['name']}"
        self._attr_unique_id = f"{safe_device_name}_pitmaster_{pitmaster.id}_{field['key']}"
        self.entity_id = f"select.{safe_device_name}_pitmaster_{pitmaster.id}_{field['key']}"
        self._attr_icon = field["icon"]
        self._attr_options = field["options"]
        self._pid_profiles = pid_profiles if pid_profiles is not None else []
        self._channel_options = channel_options if channel_options is not None else []
        self._channel_number_by_name = channel_number_by_name if channel_number_by_name is not None else {}
        self._channel_name_map = channel_name_map if channel_name_map is not None else {}
        self._attr_entity_category = EntityCategory.CONFIG

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


    def _get_pitmaster(self):
        """
        Helper to get the current pitmaster object from the coordinator data.
        """
        pitmasters = getattr(self.coordinator.data, 'pitmasters', [])
        for pm in pitmasters:
            if pm.id == self._pitmaster_id:
                return pm
        return None

    @property
    def current_option(self):
        """
        Return the currently selected option for this pitmaster field.
        """
        pitmaster = self._get_pitmaster()
        if not pitmaster:
            return None
        if self._field["key"] == "pid" and self._pid_profiles:
            pid_id = getattr(pitmaster, "pid", None)
            for p in self._pid_profiles:
                if hasattr(p, "id") and p.id == pid_id:
                    return p.name
            return None
        if self._field["key"] == "channel":
            coordinator = self.coordinator
            channels = getattr(coordinator.data, 'channels', [])
            channel_name_map = {ch.number: ch.name for ch in channels}
            self._attr_options = [ch.name for ch in channels]
            channel_value = getattr(pitmaster, "channel", None)
            return channel_name_map.get(channel_value, str(channel_value))
        return getattr(pitmaster, self._field["key"], None)

    async def async_select_option(self, option):
        """
        Handle user selecting an option for this pitmaster field.
        Updates the pitmaster via the API and refreshes coordinator data.
        """
        api = self.coordinator.hass.data[DOMAIN][self.coordinator.config_entry.entry_id]["api"]
        pitmaster = self._get_pitmaster()
        if not pitmaster:
            import logging
            logging.getLogger(__name__).error(f"[WLANThermo] PitmasterSelect: Pitmaster {self._pitmaster_id} not found for select_option")
            return
        pitmaster_data = {
            "id": pitmaster.id,
            "channel": pitmaster.channel,
            "pid": pitmaster.pid,
            "value": pitmaster.value,
            "set": pitmaster.set,
            "typ": pitmaster.typ,
        }
        if self._field["key"] == "typ":
            pitmaster_data["typ"] = option
        elif self._field["key"] == "pid" and self._pid_profiles:
            for p in self._pid_profiles:
                if hasattr(p, "name") and p.name == option:
                    pitmaster_data["pid"] = p.id
                    break
        elif self._field["key"] == "channel" and self._channel_number_by_name:
            channel_number = self._channel_number_by_name.get(option)
            if channel_number is not None:
                pitmaster_data["channel"] = channel_number
        await api.async_set_pitmaster(pitmaster_data)
        await self.coordinator.async_request_refresh()
