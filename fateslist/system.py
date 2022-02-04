from .http import BaseHTTP
from .classes import Stats, StatsFull, Vanity

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
    
    async def blstats_full(self):
        """
        Returns "stats page" (full bot list stats)
        """
        api_res = await self.request(
            method="GET",
            endpoint="/blstats-full",
        )

        if not api_res.success:
            return api_res
        return StatsFull(api_res.json)

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
    
    async def get_vote_reminders(self):
        """
        Returns the vote reminders as a list of dicts
        """
        api_res = await self.request(
            method="GET",
            endpoint="/vote-reminders",
        )

        if not api_res.success:
            return api_res
        return api_res.json