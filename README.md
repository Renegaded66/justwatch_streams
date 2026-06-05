# JustWatch Streams

<p align="center">
  <img src="logo.png" width="160" alt="logo">
</p>

Home Assistant custom integration that keeps track of when your favorite films become available on the streaming services you actually use.

Instead of manually checking multiple platforms, this integration monitors JustWatch and creates sensors in Home Assistant for each film. You can use them in dashboards, notifications, or automations to instantly know when a movie becomes available on one of your preferred providers.

## Installation (HACS)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Renegaded66&repository=justwatch_streams&category=integration)

*(Since this integration is not in the default HACS repository list, the button above will open your Home Assistant instance and prompt you to add it as a custom repository).*

### Manual Installation

If the button doesn't work, you can add it manually:

1. Open **HACS** in Home Assistant.
2. Go to **Integrations**.
3. Click **⋮ → Custom repositories** (top right corner).
4. Add `https://github.com/Renegaded66/justwatch_streams` as a custom repository and select **Integration** as the category.
5. Click **Add**.
6. Search for **JustWatch Streams** in HACS and install it.
7. Restart Home Assistant.


After restarting:

1. Go to **Settings > Devices & services > Add integration**.
2. Add **JustWatch Streams** and select your preferred streaming providers.

Only one main JustWatch Streams service can be configured. Use **Configure providers** on the integration entry to change the preferred providers later.

## Add films

Open the JustWatch Streams integration entry and use **Add film**. Enter the JustWatch URL for a film, for example:

```text
https://www.justwatch.com/de/Film/Cars
```

Each film creates one binary sensor:

- `on`: the film is available through at least one preferred subscription provider.
- `off`: it is not available through the selected subscription providers.

## Attributes

Each film sensor exposes useful attributes:

- `free_streaming_providers`: selected subscription providers where the film is available.
- `subscription_providers`: all subscription providers found on JustWatch.
- `rent_providers`: providers where the film can be rented.
- `buy_providers`: providers where the film can be bought.
- `all_offers`: parsed offer details including type, price, currency, and URL.

## Updates

Films are refreshed when Home Assistant starts and every day at `00:00` local Home Assistant time.

## Notes

JustWatch page structure can change. This integration currently parses the structured JSON-LD data embedded in the film page.
