
"""Config flow for WLANThermo BBQ integration."""

from homeassistant import config_entries
from .const import DOMAIN, MODELS
import voluptuous as vol
from homeassistant.core import callback
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.selector  import (
    BooleanSelector,
)
import aiohttp
from .api import WlanthermoBBQApi
from .data import SettingsData

CONF_PATH_PREFIX = "path_prefix"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WLANThermo."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        show_auth_fields = False
        if user_input is not None:
            # All fields are required
            if not user_input.get(CONF_HOST):
                errors[CONF_HOST] = "required"
            if not user_input.get(CONF_PORT):
                errors[CONF_PORT] = "required"
            if not user_input.get(CONF_PATH_PREFIX):
                errors[CONF_PATH_PREFIX] = "required"
            if user_input.get("auth_required", False):
                show_auth_fields = True
                if not user_input.get("username"):
                    errors["username"] = "required"
                if not user_input.get("password"):
                    errors["password"] = "required"
            if not errors:
                self.context["user_input"] = user_input
                return await self.async_step_device_info()

        base_schema = {
            vol.Required("device_name", default="WLANThermo BBQ"): str,
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=80): int,
            vol.Required(CONF_PATH_PREFIX, default="/"): str,
                vol.Required(
                    "show_inactive_unavailable",
                    default=True,
                    description={"translation_key": "show_inactive_unavailable"}
                ): BooleanSelector({}),
            vol.Required(
                "auth_required",
                  default=False,
                    description={
                        "suggested_value": False,
                          "translation_key": "auth_required"
                          }
            ): BooleanSelector({}),
            vol.Optional("username", default=""): str,
            vol.Optional("password", default=""): str,
        }
        data_schema = vol.Schema(base_schema)
        # Only require username/password if auth_required is true
        if user_input is not None and user_input.get("auth_required", False):
            if not user_input.get("username"):
                errors["username"] = "required"
            if not user_input.get("password"):
                errors["password"] = "required"

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders=None,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WlanthermoBBQOptionsFlow(config_entry)
    
    async def async_step_device_info(self, user_input=None):
        # Get user_input from context
        user_input = self.context.get("user_input")
        device_name = user_input.get("device_name", "WLANThermo BBQ")
        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        path_prefix = user_input[CONF_PATH_PREFIX]
        # Fetch /settings
        async with aiohttp.ClientSession() as session:
            api = WlanthermoBBQApi(host, port, path_prefix)
            api.set_session(session)
            settings_json = await api.get_settings()
        if not settings_json:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("device_name", default=device_name): str,
                    vol.Required(CONF_HOST, default=host): str,
                    vol.Required(CONF_PORT, default=port): int,
                    vol.Required(CONF_PATH_PREFIX, default=path_prefix): str,
                    vol.Required(
                        "show_inactive_unavailable",
                        default=True,
                        description={"translation_key": "show_inactive_unavailable"}
                    ): BooleanSelector({}),
                    vol.Required(
                        "auth_required",
                        default=False,
                            description={
                                "suggested_value": False,
                                "translation_key": "auth_required"
                                }
                    ): BooleanSelector({}),
                    vol.Optional("username", default=""): str,
                    vol.Optional("password", default=""): str,
                }),
                errors={"base": "cannot_connect"},
            )
        settings = SettingsData.from_json(settings_json)
        device = settings.device
        description = (
            f"Geräte-Info:\n"
            f"Gerät: {device.device}\n"
            f"Seriennummer: {device.serial}\n"
            f"CPU: {device.cpu}\n"
            f"HW-Version: {device.hw_version}\n"
            f"SW-Version: {device.sw_version}"
        )
        return self.async_create_entry(title=device_name, data=user_input)

class WlanthermoBBQOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        show_auth_fields = False
        if user_input is not None:
            if not user_input.get(CONF_HOST):
                errors[CONF_HOST] = "required"
            if not user_input.get(CONF_PORT):
                errors[CONF_PORT] = "required"
            if not user_input.get("scan_interval"):
                errors["scan_interval"] = "required"
            if user_input.get("auth_required", False):
                show_auth_fields = True
                if not user_input.get("username"):
                    errors["username"] = "required"
                if not user_input.get("password"):
                    errors["password"] = "required"
            if not errors:
                return self.async_create_entry(title="Options", data=user_input)

        base_schema = {
            vol.Required(CONF_HOST, default=self._config_entry.data.get(CONF_HOST, "")): str,
            vol.Required(CONF_PORT, default=self._config_entry.data.get(CONF_PORT, 80)): int,
            vol.Required("scan_interval", default=self._config_entry.options.get("scan_interval", 10)): int,
        
            vol.Required(
                "show_inactive_unavailable",
                default=self._config_entry.options.get("show_inactive_unavailable", True),
                description={"translation_key": "show_inactive_unavailable"}
            ): BooleanSelector({}),
        
            vol.Required(
                "auth_required",
                default=self._config_entry.options.get("auth_required", False),
                description={"translation_key": "auth_required"}
            ): BooleanSelector({}),
        
            vol.Optional("username", default=self._config_entry.options.get("username", "")): str,
            vol.Optional("password", default=self._config_entry.options.get("password", "")): str,
        }

        data_schema = vol.Schema(base_schema)
        # Only require username/password if auth_required is true
        if user_input is not None and user_input.get("auth_required", False):
            if not user_input.get("username"):
                errors["username"] = "required"
            if not user_input.get("password"):
                errors["password"] = "required"

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not user_input.get(CONF_HOST):
                errors[CONF_HOST] = "required"
            if not user_input.get(CONF_PORT):
                errors[CONF_PORT] = "required"
            if not user_input.get(CONF_PATH_PREFIX):
                errors[CONF_PATH_PREFIX] = "required"
            if not errors:
                self.context["user_input"] = user_input
                return await self.async_step_device_info()

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=80): int,
            vol.Required(CONF_PATH_PREFIX, default="/"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders=None,
        )

    async def async_step_device_info(self, user_input=None):
        # Get user_input from context
        user_input = self.context.get("user_input")
        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        path_prefix = user_input[CONF_PATH_PREFIX]
        # Fetch /settings
        async with aiohttp.ClientSession() as session:
            api = WlanthermoBBQApi(host, port, path_prefix)
            api.set_session(session)
            settings_json = await api.get_settings()
        if not settings_json:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_HOST, default=host): str,
                    vol.Required(CONF_PORT, default=port): int,
                    vol.Required(CONF_PATH_PREFIX, default=path_prefix): str,
                }),
                errors={"base": "cannot_connect"},
            )
        settings = SettingsData.from_json(settings_json)
        device = settings.device
        # Show info to user before creating entry
        description = (
            f"Geräte-Info:\n"
            f"Gerät: {device.device}\n"
            f"Seriennummer: {device.serial}\n"
            f"CPU: {device.cpu}\n"
            f"HW-Version: {device.hw_version}\n"
            f"SW-Version: {device.sw_version}"
        )
        if user_input is not None and user_input.get("confirm"):
            return self.async_create_entry(title=host, data=user_input)
        # Confirm step
        return self.async_show_form(
            step_id="device_info",
            data_schema=vol.Schema({vol.Required("confirm", default=True): bool}),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return WlanthermoBBQOptionsFlow(config_entry)
