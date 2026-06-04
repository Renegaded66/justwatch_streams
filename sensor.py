from homeassistant.components.sensor import SensorEntity

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data["justwatch_streams"][entry.entry_id]

    async_add_entities([
        JustWatchSensor(coordinator)
    ])


class JustWatchSensor(SensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = "JustWatch Streams"
        self._attr_unique_id = "justwatch_streams_main"

    @property
    def state(self):
        return len(self.coordinator.data or [])