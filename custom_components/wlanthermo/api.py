"""
API client for WLANThermo device.
Provides asynchronous methods to interact with the WLANThermo device's REST API.
Handles data retrieval and configuration updates for channels and pitmasters.
"""

import async_timeout
from homeassistant.helpers.update_coordinator import UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import logging

class WLANThermoApi:
    """
    Asynchronous API client for WLANThermo device.
    Handles HTTP communication for data and configuration endpoints.
    """
    def __init__(self, hass, host, port=80, path_prefix="/"):
        """
        Initialize the API client.
        :param host: Device hostname or IP
        :param port: HTTP port (default 80)
        :param path_prefix: API path prefix (default '/')
        """
        self._hass = hass
        self._host = host
        self._port = port
        self._path_prefix = path_prefix.rstrip("/")
        self._base_url = f"http://{host}:{port}{self._path_prefix}"

    async def _get(self, endpoint):
        _LOGGER = logging.getLogger(__name__)
        url = f"{self._base_url}{endpoint}"

        session = async_get_clientsession(self._hass)

        try:
            async with async_timeout.timeout(10):
                async with session.get(url, allow_redirects=True) as resp:
                    if resp.status != 200:
                        _LOGGER.error(f"WLANThermoApi: result {url}: {resp.status} <-1")
                        return None

                    try:
                        data = await resp.json()
                        return data
                    except Exception as json_err:
                        _LOGGER.error(f"WLANThermoApi: JSON decode error for {url}: {json_err} <-2")
                        return None

        except Exception as err:
            _LOGGER.error(f"WLANThermoApi: Error fetching {url}: {err} <-3")
            return None


    async def get_data(self):
        return await self._get("/data")

    async def get_settings(self):
        """
        Fetch device settings (configuration, device info, etc).
        :return: JSON data or None
        """
        return await self._get("/settings")

    async def get_info(self):
        """
        Fetch general device info (if available).
        :return: JSON data or None
        """
        return await self._get("/info")

    async def async_set_channel(self, channel_data: dict, method: str = "POST") -> bool:
        """
        Send channel configuration to the device.
        """
        session = async_get_clientsession(self._hass)
        url = f"{self._base_url}/setchannels"
        headers = {"Content-Type": "application/json"}

        try:
            async with async_timeout.timeout(10):
                request = getattr(session, method.lower())
                async with request(url, json=channel_data, headers=headers) as resp:
                    text = await resp.text()
                    return resp.status == 200 and text.strip().lower() == "true"
        except Exception as err:
            _LOGGER = logging.getLogger(__name__)
            _LOGGER.debug("set_channel failed: %s", err)
            return False


    async def async_set_pitmaster(self, pitmaster_data: dict, method: str = "POST") -> bool:
        """
        Send pitmaster configuration to the device.
        :param pitmaster_data: dict representing a single pitmaster object (will be wrapped in a list)
        :param method: HTTP method ('POST' or 'PUT')
        :return: True if successful, False otherwise
        """
        session = async_get_clientsession(self._hass)
        url = f"{self._base_url}/setpitmaster"
        headers = {"Content-Type": "application/json"}
        # Add authentication if needed (e.g., token)
        # headers["Authorization"] = f"Bearer {self._token}"
        try:
            async with async_timeout.timeout(10):
                # Select HTTP method dynamically
                req = getattr(session, method.lower())
                # The API expects a list of pitmaster objects
                async with req(url, json=[pitmaster_data], headers=headers) as resp:
                    text = await resp.text()
                    return resp.status == 200 and text.strip().lower() == "true"
        except Exception as err:
            _LOGGER = logging.getLogger(__name__)
            _LOGGER.debug("set_pitmaster failed: %s", err)
            return False
