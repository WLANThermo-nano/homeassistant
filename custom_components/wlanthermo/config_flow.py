
"""
Config flow for WLANThermo integration.
Handles user and options configuration steps for the Home Assistant integration.
Guides the user through device connection, authentication, and device info retrieval.
"""

from homeassistant import config_entries
from .const import DOMAIN
import voluptuous as vol
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.selector  import (
    BooleanSelector,
)

CONF_PATH_PREFIX = "path_prefix"

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Handle a config flow for WLANThermo.
    Guides the user through the initial setup and device info retrieval.
    """
    VERSION = 1
    def _schema(self, user_input=None):
        user_input = user_input or {}

        schema = {
            vol.Required("device_name", default=user_input.get("device_name", "WLANThermo")): str,
            vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
            vol.Required(CONF_PORT, default=user_input.get(CONF_PORT, 80)): int,
            vol.Required(CONF_PATH_PREFIX, default=user_input.get(CONF_PATH_PREFIX, "/")): str,
            vol.Required(
                "show_inactive_unavailable",
                default=user_input.get("show_inactive_unavailable", True),
                description={"translation_key": "show_inactive_unavailable"}
            ): BooleanSelector({}),
            vol.Required(
                "auth_required",
                default=user_input.get("auth_required", False),
                description={"translation_key": "auth_required"}
            ): BooleanSelector({}),
        }

        if user_input.get("auth_required"):
            schema.update({
                vol.Required("username", default=user_input.get("username", "")): str,
                vol.Required("password", default=user_input.get("password", "")): str,
            })

        return vol.Schema(schema)

    async def async_step_user(self, user_input=None):
        """
        First step of the config flow: collect connection and authentication info from the user.
        Validates required fields and optionally prompts for authentication.
        """
        errors = {}

        if user_input is not None:
            if user_input.get("auth_required"):
                if not user_input.get("username"):
                    errors["username"] = "required"
                if not user_input.get("password"):
                    errors["password"] = "required"

            if not errors:
                self.context["user_input"] = user_input
                return await self.async_step_device_info()

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(user_input),
            errors=errors,
        )


    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """
        Return the options flow handler for this config entry.
        """
        return WLANThermoOptionsFlow(config_entry)

    async def async_step_device_info(self, user_input=None):
        """
        Second step: fetch device info from the device and confirm connection.
        """
        from .api import WLANThermoApi
        from .data import SettingsData

        user_input = self.context.get("user_input")

        device_name = user_input.get("device_name", "WLANThermo")
        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        path_prefix = user_input[CONF_PATH_PREFIX]
        auth_required = user_input.get("auth_required", False)

        #async with aiohttp.ClientSession() as session:
        api = WLANThermoApi(
            self.hass,
            host,
            port,
            path_prefix,
        )

        if auth_required:
            api.set_auth(
                user_input.get("username"),
                user_input.get("password"),
            )

        try:
            settings_json = await api.get_settings()
        except Exception:
            settings_json = None

        if not settings_json:
            schema = {
                vol.Required("device_name", default=device_name): str,
                vol.Required(CONF_HOST, default=host): str,
                vol.Required(CONF_PORT, default=port): int,
                vol.Required(CONF_PATH_PREFIX, default=path_prefix): str,
                vol.Required(
                    "show_inactive_unavailable",
                    default=user_input.get("show_inactive_unavailable", True),
                    description={"translation_key": "show_inactive_unavailable"},
                ): BooleanSelector({}),
                vol.Required(
                    "auth_required",
                    default=auth_required,
                    description={"translation_key": "auth_required"},
                ): BooleanSelector({}),
            }

            if auth_required:
                schema[vol.Required("username")] = str
                schema[vol.Required("password")] = str

            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(schema),
                errors={"base": "cannot_connect"},
            )

        settings = SettingsData.from_json(settings_json)
        device = settings.device

        unique_id = device.serial or f"{host}:{port}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        # 🔥 clean stored data
        clean_data = dict(user_input)
        if not auth_required:
            clean_data.pop("username", None)
            clean_data.pop("password", None)

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
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """
        First step of the options flow: allow user to update connection and polling options.
        Validates required fields and authentication if enabled.
        """
        errors = {}

        if user_input is not None:
            auth_required = user_input.get("auth_required", False)

            if auth_required:
                if not user_input.get("username"):
                    errors["username"] = "required"
                if not user_input.get("password"):
                    errors["password"] = "required"

            if not errors:
                clean = dict(user_input)
                if not auth_required:
                    clean.pop("username", None)
                    clean.pop("password", None)

                return self.async_create_entry(
                    title="Options",
                    data=clean,
                )

        options = self._config_entry.options
        data = self._config_entry.data

        schema = {
            vol.Required(
                CONF_HOST,
                default=options.get(CONF_HOST, data.get(CONF_HOST)),
            ): str,
            vol.Required(
                CONF_PORT,
                default=options.get(CONF_PORT, data.get(CONF_PORT, 80)),
            ): int,
            vol.Required(
                CONF_PATH_PREFIX,
                default=options.get(CONF_PATH_PREFIX, data.get(CONF_PATH_PREFIX, "/")),
            ): str,
            vol.Required(
                "scan_interval",
                default=options.get("scan_interval", 10),
            ): int,
            vol.Required(
                "show_inactive_unavailable",
                default=options.get("show_inactive_unavailable", True),
                description={"translation_key": "show_inactive_unavailable"},
            ): BooleanSelector({}),
            vol.Required(
                "auth_required",
                default=options.get("auth_required", False),
                description={"translation_key": "auth_required"},
            ): BooleanSelector({}),
        }

        if (user_input and user_input.get("auth_required")) or options.get("auth_required"):
            schema[vol.Required("username", default=options.get("username", ""))] = str
            schema[vol.Required("password", default=options.get("password", ""))] = str

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
            errors=errors,
        )
