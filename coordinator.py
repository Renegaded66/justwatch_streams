from __future__ import annotations

from datetime import date
import json
import logging

from aiohttp import ClientError
from bs4 import BeautifulSoup

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_PROVIDERS, CONF_URL, PROVIDER_ALIASES

_LOGGER = logging.getLogger(__name__)

OFFER_SUBSCRIPTION = "subscription"
OFFER_RENT = "rent"
OFFER_BUY = "buy"
OFFER_OTHER = "other"


class JustWatchCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, subentry):
        super().__init__(
            hass,
            _LOGGER,
            name=f"justwatch_streams_{subentry.subentry_id}",
            update_interval=None,
        )
        self.entry = entry
        self.subentry = subentry

    async def _async_update_data(self):
        url = self.subentry.data[CONF_URL]
        session = async_get_clientsession(self.hass)

        try:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20) as resp:
                html = await resp.text()
                if resp.status >= 400:
                    return self._empty_data(
                        f"JustWatch returned HTTP {resp.status}",
                        title=self.subentry.title,
                    )
        except TimeoutError:
            return self._empty_data("Timed out while fetching JustWatch", title=self.subentry.title)
        except ValueError:
            return self._empty_data("Invalid JustWatch URL", title=self.subentry.title)
        except ClientError as err:
            return self._empty_data(f"Could not fetch JustWatch: {err.__class__.__name__}", title=self.subentry.title)

        return self._parse(html)

    def _parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", {"type": "application/ld+json"})
        if script is None or script.string is None:
            return self._empty_data("No JSON-LD metadata found", title=self.subentry.title)

        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            return self._empty_data("Could not parse JSON-LD metadata", title=self.subentry.title)

        offers = []
        seen = set()

        for action in data.get("potentialAction", []):
            offer = action.get("expectsAcceptanceOf")
            if not isinstance(offer, dict):
                continue

            # Skip if the offer is not yet available
            availability = offer.get("availability")
            if isinstance(availability, str) and "NotYetAvailable" in availability:
                continue

            valid_from = offer.get("validFrom")
            if isinstance(valid_from, str):
                try:
                    if len(valid_from) >= 10:
                        valid_date = date.fromisoformat(valid_from[:10])
                        if valid_date > date.today():
                            continue
                except ValueError:
                    pass

            provider = self._provider_name(offer)
            if provider is None:
                continue

            offer_type = self._offer_type(offer)
            stream = {
                "provider": provider,
                "type": offer_type,
                "price": offer.get("price"),
                "currency": offer.get("priceCurrency"),
                "category": offer.get("category"),
                "url": action.get("target", {}).get("urlTemplate"),
            }
            key = (stream["provider"], stream["type"], stream["price"], stream["url"])
            if key in seen:
                continue

            seen.add(key)
            offers.append(stream)

        subscription_offers = [
            offer for offer in offers if offer["type"] == OFFER_SUBSCRIPTION
        ]
        selected_providers = self.entry.options.get(
            CONF_PROVIDERS,
            self.entry.data.get(CONF_PROVIDERS, []),
        )
        matched_streams = [
            offer for offer in subscription_offers
            if self._matches_selected_provider(offer["provider"], selected_providers)
        ]

        return {
            "available": bool(matched_streams),
            "title": data.get("name") or self.subentry.title,
            "offers": offers,
            "streams": subscription_offers,
            "matched_streams": matched_streams,
            "rent_offers": [offer for offer in offers if offer["type"] == OFFER_RENT],
            "buy_offers": [offer for offer in offers if offer["type"] == OFFER_BUY],
            "error": None,
        }

    @staticmethod
    def _empty_data(error, title):
        return {
            "available": False,
            "title": title,
            "offers": [],
            "streams": [],
            "matched_streams": [],
            "rent_offers": [],
            "buy_offers": [],
            "error": error,
        }

    @staticmethod
    def _offer_type(offer):
        business_function = str(offer.get("businessFunction", "")).lower()
        action_type = str(offer.get("@type", "")).lower()

        if "provideservice" in business_function or "provide service" in business_function:
            return OFFER_SUBSCRIPTION
        if "rent" in business_function or "lease" in business_function or "rent" in action_type:
            return OFFER_RENT
        if "sell" in business_function or "buy" in action_type:
            return OFFER_BUY
        return OFFER_OTHER

    @staticmethod
    def _provider_name(offer):
        offered_by = offer.get("offeredBy") or offer.get("seller")
        if not isinstance(offered_by, dict):
            return None
        return offered_by.get("name")

    @staticmethod
    def _matches_selected_provider(provider, selected_providers):
        normalized_provider = provider.lower()
        for selected_provider in selected_providers:
            aliases = PROVIDER_ALIASES.get(selected_provider, ())
            if any(alias in normalized_provider for alias in aliases):
                return True
        return False
