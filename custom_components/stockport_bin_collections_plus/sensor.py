"""Sensor platform for Stockport Bin Collections."""

from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BIN_COLOURS, DOMAIN
from .coordinator import StockportBinCoordinator

ICONS = {
    "blue": "mdi:trash-can",
    "brown": "mdi:trash-can",
    "green": "mdi:trash-can",
    "black": "mdi:trash-can",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[StockportBinCoordinator],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up collection sensors from a config entry."""
    coordinator = entry.runtime_data
    async_add_entities(
        StockportBinSensor(coordinator, entry, colour)
        for colour in BIN_COLOURS
        if colour in coordinator.data
    )


class StockportBinSensor(CoordinatorEntity[StockportBinCoordinator], SensorEntity):
    """A sensor containing the next date for one bin colour."""

    _attr_device_class = SensorDeviceClass.DATE
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: StockportBinCoordinator,
        entry: ConfigEntry[StockportBinCoordinator],
        colour: str,
    ) -> None:
        super().__init__(coordinator)
        self._colour = colour
        self._attr_name = f"{colour.title()} bin"
        self._attr_unique_id = f"{entry.entry_id}_{colour}"
        self._attr_icon = ICONS[colour]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Stockport bin collections Plus",
            manufacturer="Stockport Council",
            model="Bin collection service",
            configuration_url=entry.data["collection_url"],
        )

    @property
    def native_value(self) -> date | None:
        """Return the next collection date."""
        return self.coordinator.data.get(self._colour)
