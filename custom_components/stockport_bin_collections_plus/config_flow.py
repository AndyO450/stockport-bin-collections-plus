"""Config flow for Stockport Bin Collections."""

from __future__ import annotations

from hashlib import sha256
from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    StockportBinApi,
    StockportBinConnectionError,
    StockportBinInvalidResponseError,
)
from .const import ALLOWED_HOST, CONF_COLLECTION_URL, DOMAIN


class StockportBinConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Stockport Bin Collections."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_COLLECTION_URL].strip()
            parsed = urlparse(url)
            if (
                parsed.scheme != "https"
                or parsed.hostname != ALLOWED_HOST
                or not parsed.path.startswith("/bin-collections/show/")
            ):
                errors[CONF_COLLECTION_URL] = "invalid_url"
            else:
                api = StockportBinApi(async_get_clientsession(self.hass), url)
                try:
                    await api.async_get_collections()
                except StockportBinConnectionError:
                    errors["base"] = "cannot_connect"
                except StockportBinInvalidResponseError:
                    errors["base"] = "invalid_response"
                else:
                    unique_id = sha256(url.encode()).hexdigest()[:16]
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="Stockport bin collections Plus",
                        data={CONF_COLLECTION_URL: url},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_COLLECTION_URL): str}
            ),
            errors=errors,
        )
