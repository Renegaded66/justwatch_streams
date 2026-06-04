import aiohttp
from .const import TMDB_BASE_URL


class TMDbClient:
    def __init__(self, api_key: str, session: aiohttp.ClientSession):
        self.api_key = api_key
        self.session = session

    async def search_movie(self, query: str):
        url = f"{TMDB_BASE_URL}/search/movie"
        params = {"api_key": self.api_key, "query": query}

        async with self.session.get(url, params=params) as resp:
            data = await resp.json()
            return data.get("results", [])

    async def get_watch_providers(self, movie_id: int):
        url = f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers"
        params = {"api_key": self.api_key}

        async with self.session.get(url, params=params) as resp:
            data = await resp.json()
            return data.get("results", {})