"""
Home Assistant integration for WLANThermodevices.
Handles setup, teardown, and data coordination for the integration.
"""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, CONF_MODEL
from .api import WLANThermoApi
from .data import WlanthermoData, SettingsData
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging
import asyncio

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
	"""
	Set up a WLANThermo integration entry.
	Initializes API, fetches device info, sets up data coordinator, and forwards platforms.
	"""
	hass.data.setdefault(DOMAIN, {})

	# Retrieve connection and configuration options
	host = entry.options.get("host", entry.data.get("host"))
	port = entry.options.get("port", entry.data.get("port", 80))
	path_prefix = entry.data.get("path_prefix", "/")
	scan_interval = entry.options.get("scan_interval", 10)

	api = WLANThermoApi(hass, host, port, path_prefix)


	device_name = entry.data.get("device_name", "WLANThermo")
	
	device_info = DeviceInfo(
		identifiers={(DOMAIN, entry.entry_id)},
		name=device_name,
		manufacturer="WLANThermo",
		model=entry.data.get(CONF_MODEL, "unknown"),
	)

	try:
		# First check if device is online
		probe = await api.get_data()

		settings_json = None
		settings = None

		if probe:
			# Device is online → safe to fetch settings
			try:
				settings_json = await api.get_settings()
				if settings_json:
					settings = SettingsData.from_json(settings_json)
					api.settings = settings
			except Exception as e:
				_LOGGER.error(f"WLANThermo: Failed to fetch /settings: {e}")

		# Build device_info
		if settings and hasattr(settings, "device"):
			dev = settings.device
			device_info = DeviceInfo(
				identifiers={(DOMAIN, entry.entry_id)},
				name=device_name,
				manufacturer="WLANThermo",
				model=f"{dev.device} {dev.hw_version}".strip(),
				sw_version=getattr(dev, "sw_version", None),
			)

	except Exception as err:
		_LOGGER.warning("Failed to fetch device info: %s", err)
		device_info = DeviceInfo(
			identifiers={(DOMAIN, entry.entry_id)},
			name=device_name,
			manufacturer="WLANThermo",
			model="unknown",
			sw_version="unknown",
		)


	async def async_update_data():
		"""
		Fetch both /data and /settings.
		Do NOT raise UpdateFailed when device is offline.
		"""
		try:
			raw_data = await api.get_data()
			if not raw_data:
				raise UpdateFailed("WLANThermo: /data returned no data")

			settings = None
			try:
				raw_settings = await api.get_settings()
				if raw_settings:
					settings = SettingsData.from_json(raw_settings)
			except Exception:
				_LOGGER.debug("WLANThermo: Device offline (no /settings)")

			return WlanthermoData(
				raw=raw_data,
				settings=settings,
			)

		except Exception as exc:
			raise UpdateFailed(f"WLANThermo offline: {exc}")

	# Set up the coordinator to periodically fetch data
	coordinator = DataUpdateCoordinator(
		hass,
		_LOGGER,
		name="WLANThermoData",
		update_method=async_update_data,
		update_interval=timedelta(seconds=scan_interval),
	)
	coordinator.api = api
	await coordinator.async_config_entry_first_refresh()


	# Prepare entry_data early so listener can use it
	entry_data = {
		"scan_interval": scan_interval,
		"coordinator": coordinator,
		"platforms_setup": set(),
		"entities": {}, 
		"device_info": device_info,
    	"api": api, 
	}
	hass.data[DOMAIN][entry.entry_id] = entry_data
	
	platforms = ["sensor", "number", "select", "text", "light"]

	# If device is offline at setup → do NOT load platforms
	if not coordinator.last_update_success:

		async def _async_start_platforms():
			if coordinator.last_update_success:
				await hass.config_entries.async_forward_entry_setups(entry, platforms)

		coordinator.async_add_listener(_async_start_platforms)
	else:
		await hass.config_entries.async_forward_entry_setups(entry, platforms)

	return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
	"""
	Unload a WLANThermointegration entry and all associated platforms.
	Cleans up hass.data and returns True if all platforms unloaded successfully.
	"""
	platforms = ["sensor", "number", "select", "text", "light"]

	unload_ok = await hass.config_entries.async_unload_platforms(
		entry, platforms
	)

	hass.data[DOMAIN].pop(entry.entry_id, None)
	return unload_ok

