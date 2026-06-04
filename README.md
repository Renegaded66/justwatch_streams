# JustWatch Streams

Home Assistant custom integration that tracks whether films are available on your preferred streaming services according to JustWatch.

## Setup

1. Copy this folder to `custom_components/justwatch_streams`.
2. Restart Home Assistant.
3. Go to **Settings > Devices & services > Add integration**.
4. Add **JustWatch Streams** and select your preferred streaming providers.

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
