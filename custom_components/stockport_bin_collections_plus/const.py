"""Constants for Stockport Bin Collections."""

from datetime import timedelta

DOMAIN = "stockport_bin_collections_plus"
PLATFORMS = ["sensor"]

CONF_COLLECTION_URL = "collection_url"

DEFAULT_SCAN_INTERVAL = timedelta(hours=12)
ALLOWED_HOST = "myaccount.stockport.gov.uk"
BIN_COLOURS = ("blue", "brown", "green", "black")

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
    "HomeAssistant-StockportBinCollections/1.0"
)
