"""Tests for the Stockport collection HTML parser."""

from datetime import date

from custom_components.stockport_bin_collections_plus.parser import parse_collections


def test_parse_collections() -> None:
    html = """
    <div class="service-item service-item-blue"><div>
      <h3>Blue bin</h3><p class="sub-title">Paper</p>
      <p>Monday, 21 September 2026</p>
    </div></div>
    <div class="service-item service-item-black"><div>
      <h3>Black bin</h3><p class="sub-title">Waste</p>
      <p>Monday, 28 September 2026</p>
    </div></div>
    """
    assert parse_collections(html) == {
        "blue": date(2026, 9, 21),
        "black": date(2026, 9, 28),
    }
