"""Stockport Bin Collections integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import StockportBinApi
from .const import CONF_COLLECTION_URL, PLATFORMS
from .coordinator import StockportBinCoordinator

type StockportBinConfigEntry = ConfigEntry[StockportBinCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: StockportBinConfigEntry
) -> bool:
    """Set up Stockport Bin Collections from a config entry."""
    api = StockportBinApi(
        async_get_clientsession(hass), entry.data[CONF_COLLECTION_URL]
    )
    coordinator = StockportBinCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: StockportBinConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
