"""
API client for WLANThermo device.
Provides asynchronous methods to interact with the WLANThermo device's REST API.
Handles data retrieval and configuration updates for channels and pitmasters.
"""

import async_timeout
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import BasicAuth
import logging

_LOGGER = logging.getLogger(__name__)

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

    async def _get(self, endpoint: str) -> dict | None:
        """
        Perform a GET request to the specified endpoint.
        Args:
            endpoint: API endpoint string.
        Returns:
            Parsed JSON response or None if request fails.
        """
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
                        self._LOGGER.warning("JSON decode error for %s: %s", url, json_err)
                        return None
        except Exception as err:
            self._LOGGER.debug("Error fetching %s: %s", url, err)
            return None


    async def get_data(self) -> dict | None:
        """
        Fetch device data.
        Returns:
            JSON data or None.
        """
        return await self._get("/data")

    async def get_settings(self) -> dict | None:
        """
        Fetch device settings (configuration, device info, etc).
        Returns:
            JSON data or None.
        """
        return await self._get("/settings")

    async def get_info(self) -> dict | None:
        """
        Fetch general device info (if available).
        Returns:
            JSON data or None.
        """
        return await self._get("/info")

    async def _request(self, method: str, endpoint: str, json: dict | None = None) -> tuple[int | None, str | None]:
        """
        Perform an HTTP request to the specified endpoint.
        Args:
            method: HTTP method as string (e.g., 'GET', 'POST').
            endpoint: API endpoint string.
            json: Optional JSON payload.
        Returns:
            Tuple of (status code, response text) or (None, None) if request fails.
        """
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
        Args:
            channel_data: Dictionary with channel configuration.
            method: HTTP method ('POST' or 'PUT').
        Returns:
            True if successful, False otherwise.
        """
        status, text = await self._request(method, "/setchannels", channel_data)
        return status == 200 and text and text.strip().lower() == "true"


    async def async_set_pitmaster(self, pitmaster_data: dict, method: str = "POST") -> bool:
        """
        Send pitmaster configuration to the device.
        Args:
            pitmaster_data: Dictionary representing a single pitmaster object (will be wrapped in a list).
            method: HTTP method ('POST' or 'PUT').
        Returns:
            True if successful, False otherwise.
        """
        status, text = await self._request(method, "/setpitmaster", [pitmaster_data])
        return status == 200 and text and text.strip().lower() == "true"
        
    async def async_set_pid_profile(self, pid_data: list[dict], method: str = "POST") -> bool:
        """
        Send PID configuration to the device.
        Args:
            pid_data: List of PID objects.
            method: HTTP method ('POST' or 'PUT').
        Returns:
            True if successful, False otherwise.
        """
        status, text = await self._request(method, "/setpid", pid_data)
        return status == 200 and text and text.strip().lower() == "true"

