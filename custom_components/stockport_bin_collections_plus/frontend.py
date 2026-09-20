"""Register the bundled SMBC Bin Card frontend module."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

FRONTEND_URL = "/stockport-bin-collections-plus"
FRONTEND_VERSION = "1.1.2"


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve and load the card without requiring a manual resource entry."""
    frontend_dir = Path(__file__).parent / "frontend"
    try:
        await hass.http.async_register_static_paths(
            [StaticPathConfig(FRONTEND_URL, frontend_dir, True)]
        )
    except RuntimeError:
        _LOGGER.debug("SMBC Bin Card frontend path is already registered")

    add_extra_js_url(
        hass,
        f"{FRONTEND_URL}/smbc-bin-card.js?v={FRONTEND_VERSION}",
    )
