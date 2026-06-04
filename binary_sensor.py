from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PROVIDERS, DOMAIN, PROVIDERS, SUBENTRY_FILM


async def async_setup_entry(hass, entry, async_add_entities):
    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_FILM:
            continue

        coordinator = hass.data[DOMAIN][entry.entry_id][subentry.subentry_id]
        async_add_entities(
            [JustWatchAvailabilityBinarySensor(coordinator)],
            config_subentry_id=subentry.subentry_id,
        )


class JustWatchAvailabilityBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.subentry.subentry_id}_availability"

    @property
    def name(self):
        title = (self.coordinator.data or {}).get("title") or self.coordinator.subentry.title
        return f"{title} Streaming"

    @property
    def is_on(self):
        return bool((self.coordinator.data or {}).get("available"))

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        selected_providers = self.coordinator.entry.options.get(
            CONF_PROVIDERS,
            self.coordinator.entry.data.get(CONF_PROVIDERS, []),
        )
        return {
            "title": data.get("title"),
            "error": data.get("error"),
            "selected_providers": [
                PROVIDERS.get(provider, provider) for provider in selected_providers
            ],
            "free_streaming_providers": [
                stream["provider"] for stream in data.get("matched_streams", [])
            ],
            "subscription_providers": [
                stream["provider"] for stream in data.get("streams", [])
            ],
            "rent_providers": [
                offer["provider"] for offer in data.get("rent_offers", [])
            ],
            "buy_providers": [
                offer["provider"] for offer in data.get("buy_offers", [])
            ],
            "all_offer_providers": sorted({
                offer["provider"] for offer in data.get("offers", [])
            }),
            "streams": data.get("matched_streams", []),
            "all_offers": data.get("offers", []),
        }
