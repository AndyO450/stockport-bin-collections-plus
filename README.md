# Stockport Bin Collections Plus for Home Assistant

A modern, UI-configured Home Assistant custom integration for Stockport Council bin collection dates.

It creates one date sensor for each bin shown by the council page (blue, brown, green and black). The integration uses Home Assistant's shared HTTP session, sends normal browser request headers, parses the page defensively and updates all sensors from one request every 12 hours.

## Install

### HACS custom repository

1. In HACS, open **Integrations**, then **Custom repositories**.
2. Add `https://github.com/AndyO450/stockport-bin-collections-plus` with category **Integration**.
3. Install **Stockport Bin Collections Plus** and restart Home Assistant.

### Manual

Copy `custom_components/stockport_bin_collections_plus` into your Home Assistant `config/custom_components` directory and restart Home Assistant.

## Configure

In Home Assistant, go to **Settings → Devices & services → Add integration**, search for **Stockport Bin Collections Plus**, and paste the complete council collection URL.

Use the private collection URL supplied by the Stockport Council address finder. Do not publish that URL, because it contains the property's identifier and address.

The integration validates the page before saving the entry. Collection dates are exposed as sensors with the `date` device class, making them suitable for dashboard cards and automations.

This is an unofficial community integration and is not affiliated with Stockport Metropolitan Borough Council.
