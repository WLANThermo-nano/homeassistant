"""
Home Assistant integration for WLANThermo devices.
Handles setup, teardown, and data coordination for the integration.
"""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, PLATFORMS
from .api import WLANThermoApi
from .data import BluetoothSettings, PushSettings, WlanthermoData, SettingsData
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
from typing import Any
import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
	"""
	Set up a WLANThermo integration entry.

	Initializes API, fetches device info, sets up data coordinator, and forwards platforms.

	Args:
		hass: Home Assistant instance.
		entry: Config entry for the integration.
	Returns:
		True if setup was successful, False otherwise.
	"""
	hass.data.setdefault(DOMAIN, {})
	# Retrieve connection and configuration options.
	host = entry.options.get("host", entry.data.get("host"))
	port = entry.options.get("port", entry.data.get("port", 80))
	path_prefix = entry.options.get("path_prefix", entry.data.get("path_prefix", "/"))
	scan_interval = entry.options.get("scan_interval", entry.data.get("scan_interval", 10))
	api = WLANThermoApi(hass, host, port, path_prefix)
	auth_required = entry.options.get("auth_required", entry.data.get("auth_required", False))
	if auth_required:
		api.set_auth(
			entry.options.get("username", entry.data.get("username")),
			entry.options.get("password", entry.data.get("password")),
		)
	api._consecutive_failures = 0
	api._max_failures = 3  # Grace period for failures.
	device_name = entry.data.get("device_name", "WLANThermo")
	device_info = DeviceInfo(
		identifiers={(DOMAIN, entry.entry_id)},
		name=device_name,
		manufacturer="WLANThermo",
		model="unknown",
	)
	try:
		# First check if device is online.
		probe = await api.get_data()
		settings_json = None
		settings = None
		if probe:
			# Device is online → safe to fetch settings.
			try:
				settings_json = await api.get_settings()
				if settings_json:
					settings = SettingsData.from_json(settings_json)
					api.settings = settings
			except Exception as e:
				_LOGGER.error("WLANThermo: Failed to fetch /settings: %s", e)
		# Build device_info.
		if settings and hasattr(settings, "device"):
			dev = settings.device
			device_info = DeviceInfo(
				identifiers={(DOMAIN, entry.entry_id)},
				name=device_name,
				manufacturer="WLANThermo",
				model=f"{dev.device} {dev.hw_version}".strip(),
				sw_version=dev.sw_version,
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

	async def async_update_data() -> Any:
		"""
		Fetch both /data and /settings.
		Raises UpdateFailed when device is offline.

		Returns:
			WlanthermoData object with latest data and settings.
		"""
		try:
			raw_data = await api.get_data()
			if not raw_data:
				api._consecutive_failures += 1
				_LOGGER.debug(
					"WLANThermo: No /data (%s/%s)",
					api._consecutive_failures,
					api._max_failures,
				)
				# if api._consecutive_failures < api._max_failures:
				# 	return coordinator.data
				raise UpdateFailed("WLANThermo offline (no /data)")
			api._consecutive_failures = 0
			settings = None
			push = None
			bluetooth = None
			try:
				raw_settings = await api.get_settings()
				if raw_settings:
					settings = SettingsData.from_json(raw_settings)
			except Exception:
				_LOGGER.debug("WLANThermo: Device offline (no /settings)")
			try:
				raw_push = await api.get_push()
				if raw_push:
					push = PushSettings(raw_push)
			except Exception:
				_LOGGER.debug("WLANThermo: Device offline (no /push)")
			try:
				raw_bt = await api.get_bluetooth()
				if raw_bt:
					bluetooth = BluetoothSettings.from_json(raw_bt)
			except Exception:
				_LOGGER.debug("WLANThermo: Device offline (no /getbluetooth)")

			return WlanthermoData(
				raw=raw_data,
				settings=settings,
				push=push,
				bluetooth=bluetooth,
			)
		except UpdateFailed:
			raise
		except Exception as exc:
			api._consecutive_failures += 1
			if api._consecutive_failures >= api._max_failures:
				raise UpdateFailed(f"WLANThermo offline: {exc}")
			return coordinator.data
	# Set up the coordinator to periodically fetch data.
	coordinator = DataUpdateCoordinator(
		hass,
		_LOGGER,
		name="WLANThermoData",
		update_method=async_update_data,
		update_interval=timedelta(seconds=scan_interval),
		always_update=True,
	)
	coordinator.api = api
	await coordinator.async_config_entry_first_refresh()
	# Prepare entry_data early so listener can use it.
	entry_data = {
		"scan_interval": scan_interval,
		"coordinator": coordinator,
		"platforms_setup": set(),
		"entities": {},
		"device_info": device_info,
		"api": api,
	}
	hass.data[DOMAIN][entry.entry_id] = entry_data
	# If device is offline at setup → do NOT load platforms.
	# if not coordinator.last_update_success:
	# 	async def _async_start_platforms() -> None:
	# 		"""
	# 		Listener to start platforms when device comes online.
	# 		Returns:
	# 			None.
	# 		"""
	# 		if coordinator.last_update_success:
	# 			await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
	# 	coordinator.async_add_listener(_async_start_platforms)
	# else:
	# 	await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
	await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

	entry.async_on_unload(
		entry.add_update_listener(async_reload_entry)
	)
	return True

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
	"""
	Reload a WLANThermo integration entry.

	Args:
		hass: Home Assistant instance.
		entry: Config entry for the integration.
	Returns:
		None.
	"""
	await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
	"""
	Unload a WLANThermo integration entry and all associated platforms.

	Cleans up hass.data and returns True if all platforms unloaded successfully.

	Args:
		hass: Home Assistant instance.
		entry: Config entry for the integration.
	Returns:
		True if all platforms unloaded successfully, False otherwise.
	"""
	unload_ok = await hass.config_entries.async_unload_platforms(
		entry, PLATFORMS
	)
	hass.data[DOMAIN].pop(entry.entry_id, None)
	return unload_ok
