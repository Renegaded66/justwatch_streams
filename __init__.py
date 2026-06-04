import asyncio
from types import MappingProxyType

from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change

from .const import CONF_PROVIDERS, CONF_URL, DEFAULT_NAME, DOMAIN, PROVIDERS, SUBENTRY_FILM
from .coordinator import JustWatchCoordinator

PLATFORMS = [Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    for subentry in entry.subentries.values():
        coordinator = JustWatchCoordinator(hass, entry, subentry)
        await coordinator.async_config_entry_first_refresh()
        hass.data[DOMAIN][entry.entry_id][subentry.subentry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    entry.async_on_unload(
        async_track_time_change(
            hass,
            lambda now: hass.async_create_task(_async_refresh_all_films(hass, entry)),
            hour=0,
            minute=0,
            second=0,
        )
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_refresh_all_films(hass: HomeAssistant, entry: ConfigEntry):
    coordinators = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).values()
    await asyncio.gather(
        *(coordinator.async_request_refresh() for coordinator in coordinators),
        return_exceptions=True,
    )


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry):
    if entry.version > 2:
        return False

    if entry.version == 1:
        data = dict(entry.data)
        providers = data.get(CONF_PROVIDERS, list(PROVIDERS))

        if url := data.get(CONF_URL):
            hass.config_entries.async_add_subentry(
                entry,
                ConfigSubentry(
                    data=MappingProxyType({CONF_URL: url}),
                    subentry_type=SUBENTRY_FILM,
                    title=url,
                    unique_id=url,
                ),
            )

        hass.config_entries.async_update_entry(
            entry,
            title=DEFAULT_NAME,
            data={CONF_PROVIDERS: providers},
            version=2,
        )

    return True
