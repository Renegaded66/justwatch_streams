# JustWatch Streams

Home Assistant custom integration that keeps track of when your favorite films become available on the streaming services you actually use.

Instead of manually checking multiple platforms, this integration monitors JustWatch and creates sensors in Home Assistant for each film. You can use them in dashboards, notifications, or automations to instantly know when a movie becomes available on one of your preferred providers.

## Installation (HACS)

1. Open **HACS** in Home Assistant.
2. Go to **Integrations**.
3. Click **⋮ → Custom repositories**.
4. Add this repository as a custom repository and select **Integration** as the category.
5. Search for **JustWatch Streams** in HACS and install it.
6. Restart Home Assistant.

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
