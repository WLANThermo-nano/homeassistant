"""
API client for WLANThermo device.
Provides asynchronous methods to interact with the BBQ device's REST API.
Handles data retrieval and configuration updates for channels and pitmasters.
"""

import aiohttp
import async_timeout


class WlanthermoBBQApi:
    """
    Asynchronous API client for WLANThermo device.
    Handles HTTP communication for data and configuration endpoints.
    """
    def __init__(self, host, port=80, path_prefix="/"):
        """
        Initialize the API client.
        :param host: Device hostname or IP
        :param port: HTTP port (default 80)
        :param path_prefix: API path prefix (default '/')
        """
        self._host = host
        self._port = port
        self._path_prefix = path_prefix.rstrip("/")
        self._base_url = f"http://{host}:{port}{self._path_prefix}"
        self._session = None  # aiohttp.ClientSession, set externally

    def set_session(self, session):
        """
        Set the aiohttp session to use for requests.
        :param session: aiohttp.ClientSession
        """
        self._session = session


    async def _get(self, endpoint):
        """
        Internal helper to perform a GET request to the device.
        :param endpoint: API endpoint (e.g., '/data')
        :return: Parsed JSON response or None on error
        """
        import logging
        _LOGGER = logging.getLogger(__name__)
        url = f"{self._base_url}{endpoint}"
        if self._session is None:
            raise RuntimeError("Session not set for WlanthermoBBQApi")
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as err:
            _LOGGER.error(f"WLANThermoBBQApi: Error fetching {url}: {err}")
            return None


    async def get_data(self):
        """
        Fetch current measurement and channel data from the device.
        :return: JSON data or None
        """
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
        :param channel_data: dict with channel configuration
        :param method: HTTP method ('POST', 'PUT', 'PATCH')
        :return: True if successful, False otherwise
        """
        import logging
        _LOGGER = logging.getLogger(__name__)
        if self._session is None:
            raise RuntimeError("Session not set for WlanthermoBBQApi")
        url = f"{self._base_url}/setchannels"
        headers = {"Content-Type": "application/json"}
        # Add authentication if needed (e.g., token)
        # headers["Authorization"] = f"Bearer {self._token}"
        try:
            async with async_timeout.timeout(10):
                # Select HTTP method dynamically
                if method.upper() == "POST":
                    req = self._session.post
                elif method.upper() == "PUT":
                    req = self._session.put
                elif method.upper() == "PATCH":
                    req = self._session.patch
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                # Send request and check for success
                async with req(url, json=channel_data, headers=headers) as resp:
                    text = await resp.text()
                    return resp.status == 200 and text.strip().lower() == "true"
        except Exception as err:
            _LOGGER.error(f"[WLANThermo] API: Error setting channel at {url}: {err}")
            return False

    async def async_set_pitmaster(self, pitmaster_data: dict, method: str = "POST") -> bool:
        """
        Send pitmaster configuration to the device.
        :param pitmaster_data: dict representing a single pitmaster object (will be wrapped in a list)
        :param method: HTTP method ('POST' or 'PUT')
        :return: True if successful, False otherwise
        """
        import logging
        _LOGGER = logging.getLogger(__name__)
        if self._session is None:
            raise RuntimeError("Session not set for WlanthermoBBQApi")
        url = f"{self._base_url}/setpitmaster"
        headers = {"Content-Type": "application/json"}
        # Add authentication if needed (e.g., token)
        # headers["Authorization"] = f"Bearer {self._token}"
        try:
            async with async_timeout.timeout(10):
                # Select HTTP method dynamically
                if method.upper() == "POST":
                    req = self._session.post
                elif method.upper() == "PUT":
                    req = self._session.put
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                # The API expects a list of pitmaster objects
                async with req(url, json=[pitmaster_data], headers=headers) as resp:
                    text = await resp.text()
                    return resp.status == 200 and text.strip().lower() == "true"
        except Exception as err:
            _LOGGER.error(f"[WLANThermo] API: Error setting pitmaster at {url}: {err}")
            return False
