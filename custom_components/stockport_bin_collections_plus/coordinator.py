"""Data update coordinator for Stockport Bin Collections."""

from __future__ import annotations

from datetime import date
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import StockportBinApi, StockportBinApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class StockportBinCoordinator(DataUpdateCoordinator[dict[str, date]]):
    """Coordinate a single HTTP request shared by all bin sensors."""

    def __init__(self, hass: HomeAssistant, api: StockportBinApi) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, date]:
        try:
            return await self.api.async_get_collections()
        except StockportBinApiError as err:
            raise UpdateFailed(str(err)) from err
