"""
API client for WLANThermo device.
Provides asynchronous methods to interact with the WLANThermo device's REST API.
Handles data retrieval and configuration updates for channels and pitmasters.
"""

import async_timeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import BasicAuth
import logging

class WLANThermoApi:
    """
    Asynchronous API client for WLANThermo device.
    Handles HTTP communication for data and configuration endpoints.
    """
    _LOGGER = logging.getLogger(__name__)
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
        self._auth = None
        self._base_url = f"http://{host}:{port}{self._path_prefix}"
        

    def set_auth(self, username: str, password: str):
        if username and password:
            self._auth = BasicAuth(username, password)
        else:
            self._auth = None

    async def _get(self, endpoint):
        url = f"{self._base_url}{endpoint}"

        session = async_get_clientsession(self._hass)

        try:
            async with async_timeout.timeout(10):
                async with session.get(url, allow_redirects=True, auth=self._auth) as resp:
                    if resp.status != 200:
                        return None

                    try:
                        data = await resp.json()
                        return data
                    except Exception as json_err:
                        self._LOGGER.warning(f"WLANThermoApi: JSON decode error for {url}: {json_err}")
                        return None

        except Exception as err:
            self._LOGGER.debug(f"WLANThermoApi: Error fetching {url}: {err}")
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

    async def _request(self, method, endpoint, json=None):
        session = async_get_clientsession(self._hass)
        url = f"{self._base_url}{endpoint}"

        try:
            async with async_timeout.timeout(10):
                req = getattr(session, method.lower())
                async with req(
                    url,
                    json=json,
                    auth=self._auth,
                    headers={"Content-Type": "application/json"},
                ) as resp:
                    text = await resp.text()
                    return resp.status, text
        except Exception as err:
            self._LOGGER.debug("%s failed: %s", endpoint, err)
            return None, None

    async def async_set_channel(self, channel_data: dict, method: str = "POST") -> bool:
        """
        Send channel configuration to the device.
        """
        status, text = await self._request(method, "/setchannels", channel_data)
        return status == 200 and text and text.strip().lower() == "true"


    async def async_set_pitmaster(self, pitmaster_data: dict, method: str = "POST") -> bool:
        """
        Send pitmaster configuration to the device.
        :param pitmaster_data: dict representing a single pitmaster object (will be wrapped in a list)
        :param method: HTTP method ('POST' or 'PUT')
        :return: True if successful, False otherwise
        """
        status, text = await self._request(method, "/setpitmaster", [pitmaster_data])
        return status == 200 and text and text.strip().lower() == "true"
        