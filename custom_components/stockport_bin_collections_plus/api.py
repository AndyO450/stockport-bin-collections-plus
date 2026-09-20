"""HTTP client for Stockport Council collection pages."""

from __future__ import annotations

from datetime import date

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import USER_AGENT
from .parser import CollectionParseError, parse_collections


class StockportBinApiError(Exception):
    """Base error for the Stockport bin API client."""


class StockportBinConnectionError(StockportBinApiError):
    """Raised when the council page cannot be reached."""


class StockportBinInvalidResponseError(StockportBinApiError):
    """Raised when the council page does not contain collection data."""


class StockportBinApi:
    """Fetch and parse a Stockport Council collection page."""

    def __init__(self, session: ClientSession, url: str) -> None:
        self._session = session
        self._url = url

    async def async_get_collections(self) -> dict[str, date]:
        """Return the next collection date for every bin on the page."""
        try:
            async with self._session.get(
                self._url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-GB,en;q=0.9",
                },
                timeout=30,
            ) as response:
                response.raise_for_status()
                html = await response.text()
        except (ClientError, TimeoutError, ClientResponseError) as err:
            raise StockportBinConnectionError(
                "Unable to retrieve the Stockport collection page"
            ) from err

        try:
            return parse_collections(html)
        except CollectionParseError as err:
            raise StockportBinInvalidResponseError(str(err)) from err
