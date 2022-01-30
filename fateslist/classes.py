import fateslist.config as cfg
from fateslist import api_modes, aiohttp
from typing import Union, Optional
from discord import Embed
from .utils import extract_time
import datetime

class InvalidMode(Exception):
    """Raised when you don't have the required mode (package) to perform the action such as trying to do an asynchronous API request without having aiohttp_requests installed or trying to do a webhook without fastapi+uvicorn"""
    def __init__(self, mode):
        if mode == "async":
            super().__init__("In order to use fateslist asynchronous API requests, you must have aiohttp, requests and aiohttp_requests installed")
        elif mode == "fastapi":
            super().__init__("In order to use fateslist webhooks, you must have fastapi and uvicorn installed")

class APIRatelimit(Exception):
    """Raised when you are being ratelimited by IBL. The ratelimit for posting stats is 3 requests per 5 minutes and is unknown/variable for getting stats from the API"""
    def __init__(self):
        super().__init__("You are being ratelimited by the Infinity Bots (IBL) API. For future reference, the ratelimit for posting stats is 3 requests per 5 minutes and is unknown/variable for getting stats from the API!")

class APIResponse():
    """
        APIResponse represents an API response in the fateslist library
        
        :param res: This is the raw response from the API. 
            This will be a aiohttp ClientResponse

        :param done: Whether the API response has succeeded or not

        :param success: If the API response has succeeded, this will be false. Similar to done but based on status code
        
        :param reason: The error message reported by the Fates List API

        :param message: Any messages returned by the API in the message field. Can be None if there are no messages

        :param json: The JSON object sent by the API

        :param status: The status code of the HTTP response received from the API
    """
    def __init__(self, *, res: aiohttp.ClientResponse, json: dict):
        self.res = res
        self.done = json.get("done")
        self.success = res.status < 400
        self.reason = json.get("reason")
        self.json = json
        self.status = res.status

class BaseObject():
    def __init__(self, json):
        self.__dict__.update(**json)
    
    def dict(self) -> dict:
        """Returns the class as a dict using the dict dunder property of the class"""
        return self.__dict__

class BaseUser(BaseObject):
    """
        This is a base user on fateslist from which all bots and users extend from
    """
    def __str__(self) -> str:
        """Returns the name of the bot or user"""
        try:
            return self.user.username
        except AttributeError:
            return str(self.dict())

    def __int__(self) -> int:
        """Returns the bot or user ID"""
        return self.user.id
    
class Bot(BaseUser):
    """
        Bot is internally a part of the classes module (which provides all of fateslist's base classes and functions). 
        It represents a bot on Fates List. The exact parameters of an bot may change and fateslist is designed to handle such changes automatically. 

        Please see https://api.fateslist.xyz/api/docs/redoc#operation/fetch_bot for a full list of parameters.

        You should access parameters using object notation
    """
    ...

class User(BaseUser):
    """
        User is internally a part of the classes module (which provides all of fateslist's base classes and functions). 
        It represents a user on Fates List. The exact parameters of an user may change and fateslist is designed to handle such changes automatically. 

        Please see https://api.fateslist.xyz/api/docs/redoc#operation/fetch_user for a full list of parameters.

        You should access parameters using object notation
    """
    ...

class UserVotes(BaseObject):
    """
        User is internally a part of the classes module (which provides all of fateslist's base classes and functions). 
        It represents user votes on Fates List. The exact parameters of an user votes may change and fateslist is designed to handle such changes automatically. 

        Please see https://api.fateslist.xyz/api/docs/redoc#operation/get_user_votes for a full list of parameters.

        You should access parameters using object notation
    """
    ...

class Stats(BaseObject):
    """
        Stats is internally a part of the classes module (which provides all of fateslist's base classes and functions). 
        It represents stats on Fates List. The exact parameters of stats may change and fateslist is designed to handle such changes automatically. 

        Please see https://api.fateslist.xyz/api/docs/redoc#operation/blstats for a full list of parameters.

        You should access parameters using object notation
    """
    def embed(self):
        """
        Returns a embed of fates list stats
        """
        embed = Embed(title="Bot List Stats", description="Fates List Stats")
        uptime_tuple = extract_time(datetime.timedelta(seconds=self.uptime))
        # ttvr = Time Till Votes Reset
        ttvr_tuple = extract_time(
            (datetime.datetime.now().replace(day=1, second=0, minute=0, hour=0) +
            datetime.timedelta(days=32)).replace(day=1) - datetime.datetime.now())
        uptime = "{} days, {} hours, {} minutes, {} seconds".format(*uptime_tuple)
        ttvr = "{} days, {} hours, {} minutes, {} seconds".format(*ttvr_tuple)
        embed.add_field(name="Uptime", value=uptime)
        embed.add_field(name="Time Till Votes Reset", value=ttvr)
        embed.add_field(name="Worker PID", value=str(self.pid))
        embed.add_field(name="Worker Number",
                        value=self.workers.index(self.pid) + 1)
        embed.add_field(
            name="Workers",
            value=f"{', '.join([str(w) for w in self.workers])} ({len(self.workers)} workers)",
        )
        embed.add_field(name="UP?", value=str(self.up))
        embed.add_field(name="Server Uptime", value=str(self.server_uptime))
        embed.add_field(name="Bot Count", value=str(self.bot_count))
        embed.add_field(name="Bot Count (Total)",
                        value=str(self.bot_count_total))
        return embed

class Vanity(BaseObject):
    """
        Vanoty is internally a part of the classes module (which provides all of fateslist's base classes and functions). 
        It represents vanities (slugs) on Fates List. The exact parameters of stats may change and fateslist is designed to handle such changes automatically. 

        Please see https://api.fateslist.xyz/api/docs/redoc#operation/get_vanity for a full list of parameters.

        You should access parameters using object notation
    """
    ...