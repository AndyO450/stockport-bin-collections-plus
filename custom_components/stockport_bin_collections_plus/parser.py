"""HTML parsing for Stockport Council collection pages."""

from __future__ import annotations

from datetime import date, datetime
from html.parser import HTMLParser
import re

from .const import BIN_COLOURS


class CollectionParseError(ValueError):
    """Raised when collection data cannot be found or understood."""


class _CollectionPageParser(HTMLParser):
    """Extract the collection-date paragraph from each service item."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.results: dict[str, str] = {}
        self._colour: str | None = None
        self._div_depth = 0
        self._capture_date = False
        self._date_parts: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())

        if tag == "div" and self._colour is None and "service-item" in classes:
            for colour in BIN_COLOURS:
                if f"service-item-{colour}" in classes:
                    self._colour = colour
                    self._div_depth = 1
                    break
            return

        if self._colour is not None and tag == "div":
            self._div_depth += 1

        if (
            self._colour is not None
            and tag == "p"
            and "sub-title" not in classes
            and self._colour not in self.results
        ):
            self._capture_date = True
            self._date_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_date:
            self._date_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._capture_date and self._colour is not None:
            value = " ".join("".join(self._date_parts).split())
            if value:
                self.results[self._colour] = value
            self._capture_date = False
            self._date_parts = []

        if self._colour is not None and tag == "div":
            self._div_depth -= 1
            if self._div_depth == 0:
                self._colour = None


def parse_collections(html: str) -> dict[str, date]:
    """Parse bin colours and collection dates from a council HTML response."""
    parser = _CollectionPageParser()
    parser.feed(html)

    if not parser.results:
        raise CollectionParseError("No bin collection entries were found")

    collections: dict[str, date] = {}
    for colour, value in parser.results.items():
        normalized = re.sub(r"\s+", " ", value).strip()
        try:
            collections[colour] = datetime.strptime(
                normalized, "%A, %d %B %Y"
            ).date()
        except ValueError as err:
            raise CollectionParseError(
                f"Could not parse the {colour} bin date: {normalized}"
            ) from err

    return collections
