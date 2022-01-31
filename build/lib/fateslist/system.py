import aiohttp
from .http import BaseHTTP
from .classes import Stats, Vanity

class SystemClient(BaseHTTP):
    def __init__(self):
        self.id = None # To ensure anything using id doesnt just die
        self.logged_in = False 

    async def blstats(self):
        """
        Returns bot list stats
        """
        api_res = await self.request(
            method="GET",
            endpoint="/blstats",
        )

        if not api_res.success:
            return api_res
        return Stats(api_res.json)
    
    async def get_vanity(self, code: str):
        """
        Returns the vanity url for a given code
        """
        api_res = await self.request(
            method="GET",
            endpoint=f"/code/{code}",
        )

        if not api_res.success:
            return api_res
        return Vanity(api_res.json)