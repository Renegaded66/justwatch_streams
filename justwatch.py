import requests
import json
from bs4 import BeautifulSoup


def fetch_streams(url: str, country: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    script = soup.find("script", {"type": "application/ld+json"})
    if not script:
        return {}

    data = json.loads(script.string)

    actions = data.get("potentialAction", [])

    streams = []

    for action in actions:
        if "expectsAcceptanceOf" not in action:
            continue

        offer = action["expectsAcceptanceOf"]
        seller = offer.get("offeredBy", {}).get("name")
        price = offer.get("price")
        url = action.get("target", {}).get("urlTemplate")

        # FILTER: nur "kostenlos"
        if price is None or price == 0:
            streams.append({
                "provider": seller,
                "url": url
            })

    return {
        "title": data.get("name"),
        "streams": streams
    }