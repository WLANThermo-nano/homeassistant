
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN, CONF_PATH_PREFIX, CONF_MODEL
from .api import WlanthermoBBQApi
from .data import WlanthermoData
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
	host = entry.options.get("host", entry.data.get("host"))
	port = entry.options.get("port", entry.data.get("port", 80))
	path_prefix = entry.data.get("path_prefix", "/")
	scan_interval = entry.options.get("scan_interval", 10)
	model = entry.data.get("model", "select")

	session = aiohttp_client.async_get_clientsession(hass)
	api = WlanthermoBBQApi(host, port, path_prefix)
	api.set_session(session)

	device_name = entry.data.get("device_name", "WLANThermo BBQ")
	host = entry.data.get("host")
	path_prefix = entry.data.get("path_prefix", "/")
	device_info = {}
	from .data import SettingsData
	try:
		settings_json = await api.get_settings()
		settings = None
		if settings_json:
			try:
				settings = SettingsData.from_json(settings_json)
				api.settings = settings
			except Exception as e:
				import logging
				logging.getLogger(__name__).error(f"WLANThermoBBQ: Failed to parse /settings JSON: {e}")
		if settings and hasattr(settings, "device"):
			dev = settings.device
			# Compose a descriptive model string
			model_str = f"{getattr(dev, 'device', 'unknown')} {getattr(dev, 'hw_version', '')} {getattr(dev, 'cpu', '')}".strip()
			device_info = {
				"identifiers": {(DOMAIN, dev.serial or host)},
				"name": device_name,
				"manufacturer": "WLANThermo",
				"model": model_str,
				"sw_version": getattr(dev, "sw_version", "unknown"),
			}
		else:
			model_str = f"{getattr(dev, 'device', 'unknown')} {getattr(dev, 'hw_version', '')} {getattr(dev, 'cpu', '')}".strip()
			device_info = {
				"identifiers": {(DOMAIN, host)},
				"name": device_name,
				"manufacturer": "WLANThermo",
				"model": model_str,
				"sw_version": "unknown",
			}
	except Exception:
		device_info = {
			"identifiers": {(DOMAIN, host)},
			"name": device_name,
			"manufacturer": "WLANThermo",
			"model": entry.data.get("model", "unknown"),
			"sw_version": "unknown",
		}

	import asyncio
	async def async_update_data():
		max_retries = 3
		last_exc = None
		for attempt in range(1, max_retries + 1):
			try:
				raw = await api.get_data()
				if not raw:
					raise Exception("Failed to fetch /data from device")
				return WlanthermoData(raw)
			except Exception as exc:
				last_exc = exc
				_LOGGER.warning(f"WLANThermo BBQ: Error fetching /data (attempt {attempt}): {exc}")
				await asyncio.sleep(2 * attempt)  # Exponential backoff
		raise last_exc or Exception("Unknown error fetching /data")

	class DebugDataUpdateCoordinator(DataUpdateCoordinator):
		async def _handle_coordinator_update(self) -> None:
			await super()._handle_coordinator_update()

	coordinator = DebugDataUpdateCoordinator(
		hass,
		_LOGGER,
		name="WLANThermo BBQ Data",
		update_method=async_update_data,
		update_interval=timedelta(seconds=scan_interval),
	)
	await coordinator.async_refresh()

	entry_data = {
		"api": api,
		"scan_interval": scan_interval,
		"model": model,
		"coordinator": coordinator,
		"device_info": device_info,
		"platforms_setup": set(),
	}
	hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry_data

	platforms = ["sensor", "number", "select", "text", "light"]
	await hass.config_entries.async_forward_entry_setups(entry, platforms)
	entry_data["platforms_setup"].update(platforms)
	return True

import asyncio

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
	platforms = ["sensor", "number", "select", "text", "light"]
	results = await asyncio.gather(
		*(hass.config_entries.async_forward_entry_unload(entry, platform) for platform in platforms)
	)
	hass.data[DOMAIN].pop(entry.entry_id)
	return all(results)
