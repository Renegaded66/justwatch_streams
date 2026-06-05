from typing import Any
from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_PROVIDERS,
    CONF_URL,
    DEFAULT_NAME,
    DOMAIN,
    JUSTWATCH_HOST,
    PROVIDERS,
    SUBENTRY_FILM,
)


def _providers_schema(default=None):
    return vol.Schema({
        vol.Required(CONF_PROVIDERS, default=default if default is not None else []): SelectSelector(
            SelectSelectorConfig(
                mode=SelectSelectorMode.DROPDOWN,
                multiple=True,
                options=[
                    SelectOptionDict(label=label, value=value)
                    for value, label in PROVIDERS.items()
                ],
            )
        ),
    })


def _film_schema():
    return vol.Schema({
        vol.Required(CONF_URL): str,
    })


class JustWatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        return JustWatchOptionsFlowHandler(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        errors = {}

        if user_input is not None:
            if self._async_current_entries():
                return self.async_abort(reason="single_instance_allowed")

            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={
                    CONF_PROVIDERS: user_input[CONF_PROVIDERS],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_providers_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()

        if user_input is not None:
            return self.async_update_reload_and_abort(
                entry,
                data_updates={
                    CONF_PROVIDERS: user_input[CONF_PROVIDERS],
                },
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_providers_schema(entry.data.get(CONF_PROVIDERS, list(PROVIDERS))),
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls,
        config_entry: ConfigEntry,
    ) -> dict[str, type[ConfigSubentryFlow]]:
        return {SUBENTRY_FILM: FilmSubentryFlowHandler}


class FilmSubentryFlowHandler(ConfigSubentryFlow):
    @property
    def _is_new(self):
        return self.source == "user"

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> SubentryFlowResult:
        errors = {}

        if user_input is not None:
            url = user_input[CONF_URL].strip()
            if not _is_justwatch_url(url):
                errors[CONF_URL] = "invalid_url"
            elif _is_duplicate_film_url(self._get_entry(), url):
                errors[CONF_URL] = "already_configured"
            else:
                return self.async_create_entry(
                    title=url,
                    data={CONF_URL: url},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_film_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> SubentryFlowResult:
        subentry = self._get_reconfigure_subentry()
        errors = {}

        if user_input is not None:
            url = user_input[CONF_URL].strip()
            if not _is_justwatch_url(url):
                errors[CONF_URL] = "invalid_url"
            elif _is_duplicate_film_url(self._get_entry(), url, subentry.subentry_id):
                errors[CONF_URL] = "already_configured"
            else:
                return self.async_update_and_abort(
                    self._get_entry(),
                    subentry,
                    data={CONF_URL: url},
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                _film_schema(),
                subentry.data,
            ),
            errors=errors,
        )


def _is_justwatch_url(url):
    if url.startswith("<!DOCTYPE html") or url.startswith("<html"):
        return False

    try:
        parsed_url = urlparse(cv.url(url))
    except vol.Invalid:
        return False

    hostname = parsed_url.hostname or ""
    return hostname == JUSTWATCH_HOST or hostname.endswith(f".{JUSTWATCH_HOST}")


def _is_duplicate_film_url(entry, url, current_subentry_id=None):
    return any(
        subentry.subentry_type == SUBENTRY_FILM
        and subentry.subentry_id != current_subentry_id
        and subentry.data.get(CONF_URL) == url
        for subentry in entry.subentries.values()
    )


class JustWatchOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: ConfigEntry):
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_PROVIDERS: user_input[CONF_PROVIDERS],
                },
            )

        selected_providers = self._config_entry.options.get(
            CONF_PROVIDERS,
            self._config_entry.data.get(CONF_PROVIDERS, list(PROVIDERS)),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_providers_schema(selected_providers),
        )
