
"""
Config flow for WLANThermo integration.
Handles user and options configuration steps for the Home Assistant integration.
Guides the user through device connection, authentication, and device info retrieval.
"""
from homeassistant import config_entries
from .const import DOMAIN
from .api import WLANThermoApi
import voluptuous as vol
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.selector  import (
    BooleanSelector,
)

CONF_PATH_PREFIX = "path_prefix"

# Flow helpers:
# - _validate_auth: auth field validation
# - _clean_auth: remove unused auth fields
# - _create_api: build API client from user input
# - _base_schema: shared config/options schema

def _validate_auth(user_input: dict, errors: dict) -> None:
    """
    Validate authentication fields in user input.
    Args:
        user_input: Dictionary of user input values.
        errors: Dictionary to populate with error messages.
    """
    if not user_input.get("auth_required"):
        return
    if not user_input.get("username"):
        errors["username"] = "required"
    if not user_input.get("password"):
        errors["password"] = "required"


def _clean_auth(user_input: dict) -> dict:
    """
    Remove unused authentication fields if auth is not required.
    Args:
        user_input: Dictionary of user input values.
    Returns:
        Cleaned dictionary with unused auth fields removed.
    """
    data = dict(user_input)
    if not data.get("auth_required"):
        data.pop("username", None)
        data.pop("password", None)
    return data


def _create_api(hass, user_input: dict) -> WLANThermoApi:
    """
    Build an API client from user input.
    Args:
        hass: Home Assistant instance.
        user_input: Dictionary of user input values.
    Returns:
        Configured WLANThermoApi instance.
    """
    api = WLANThermoApi(hass, user_input[CONF_HOST], user_input[CONF_PORT], user_input[CONF_PATH_PREFIX])
    if user_input.get("auth_required"):
        api.set_auth(
            user_input.get("username"),
            user_input.get("password"),
        )
    return api


def _base_schema(*, user_input: dict = None, defaults: dict = None, include_device_name: bool = False, include_scan_interval: bool = False) -> vol.Schema:
    """
    Build the base schema for config or options flow.
    Args:
        user_input: Dictionary of user input values.
        defaults: Dictionary of default values.
        include_device_name: Whether to include device name in schema.
        include_scan_interval: Whether to include scan interval in schema.
    Returns:
        voluptuous.Schema object for the form.
    """
    user_input = user_input or {}
    defaults = defaults or {}
    schema = {}
    # Add device name field if requested.
    if include_device_name:
        schema[
            vol.Required("device_name",default=user_input.get("device_name", defaults.get("device_name", "WLANThermo")))
        ] = str

    schema.update({
        vol.Required(CONF_HOST,default=user_input.get(CONF_HOST, defaults.get(CONF_HOST, ""))): str,
        vol.Required(CONF_PORT,default=user_input.get(CONF_PORT, defaults.get(CONF_PORT, 80))): int,
        vol.Required(CONF_PATH_PREFIX,default=user_input.get(CONF_PATH_PREFIX, defaults.get(CONF_PATH_PREFIX, "/"))): str,
    })

    if include_scan_interval:
        schema[
            vol.Required("scan_interval",default=user_input.get("scan_interval", defaults.get("scan_interval", 10)))
        ] = int

    schema.update({
        vol.Required(
            "show_inactive_unavailable",
            default=user_input.get("show_inactive_unavailable",defaults.get("show_inactive_unavailable", True)),
            description={"translation_key": "show_inactive_unavailable"},
        ): BooleanSelector({}),
        vol.Required(
            "auth_required",
            default=user_input.get("auth_required", defaults.get("auth_required", False)),
            description={"translation_key": "auth_required"},
        ): BooleanSelector({}),
        vol.Optional(
            "username",
            default=user_input.get("username", ""),
            description={"translation_key": "username_optional"},
        ): str,
        vol.Optional(
            "password",
            default=user_input.get("password", ""),
            description={"translation_key": "password_optional"},
        ): str,
    })

    return vol.Schema(schema)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Handle a config flow for WLANThermo.
    Guides the user through the initial setup and device info retrieval.
    """
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """
        First step of the config flow: collect connection and authentication info from the user.
        Args:
            user_input: Optional dictionary of user input values.
        Returns:
            Result of the form or next step.
        """
        errors = {}
        if user_input is not None:
            _validate_auth(user_input, errors)
            if not errors:
                self.context["user_input"] = user_input
                return await self.async_step_device_info()
        return self.async_show_form(
            step_id="user",
            data_schema=_base_schema(user_input=user_input, include_device_name=True),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry) -> 'WLANThermoOptionsFlow':
        """
        Return the options flow handler for this config entry.
        Args:
            config_entry: The config entry instance.
        Returns:
            WLANThermoOptionsFlow instance.
        """
        return WLANThermoOptionsFlow(config_entry)

    async def async_step_device_info(self, user_input: dict | None = None):
        """
        Second step: fetch device info from the device and confirm connection.
        Args:
            user_input: Optional dictionary of user input values.
        Returns:
            Result of the form or entry creation.
        """
        from .data import SettingsData
        user_input = self.context.get("user_input")
        device_name = user_input.get("device_name", "WLANThermo")
        # Create API client and fetch device settings.
        api = _create_api(self.hass, user_input)
        try:
            settings_json = await api.get_settings()
        except Exception:
            settings_json = None
        if not settings_json:
            return self.async_show_form(
                step_id="user",
                data_schema=_base_schema(user_input=user_input, include_device_name=True),
                errors={"base": "cannot_connect"},
            )
        settings = SettingsData.from_json(settings_json)
        device = settings.device
        unique_id = device.serial or f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        clean_data = _clean_auth(user_input)
        return self.async_create_entry(
            title=device_name,
            data=clean_data,
        )


class WLANThermoOptionsFlow(config_entries.OptionsFlow):
    """
    Handle the options flow for WLANThermo.
    Allows users to update connection and polling options after setup.
    """
    def __init__(self, config_entry):
        """
        Initialize the options flow handler.
        Args:
            config_entry: The config entry instance.
        """
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """
        First step of the options flow: allow user to update connection and polling options.
        Args:
            user_input: Optional dictionary of user input values.
        Returns:
            Result of the form or entry creation.
        """
        errors = {}
        if user_input is not None:
            _validate_auth(user_input, errors)
            if not errors:
                clean = _clean_auth(user_input)
                return self.async_create_entry(
                    title="Options",
                    data=clean,
                )
        defaults = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_base_schema(
                user_input=user_input,
                defaults=defaults,
                include_scan_interval=True,
            ),
            errors=errors,
        )
