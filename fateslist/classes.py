import fateslist.config as cfg
from fateslist import api_modes, aiohttp
from typing import Union, Optional

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