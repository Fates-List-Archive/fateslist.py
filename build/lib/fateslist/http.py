import fateslist.config as cfg
from fateslist.classes import APIResponse, APIRatelimit, Bot, User, UserVotes
import aiohttp
from typing import Optional
from loguru import logger
try:
    import orjson as json_lib
except:
    logger.warning("Orjson could not be imported... falling back to json. Performance will be decreased")
    import json as json_lib

class BaseHTTP():
    user_agent = f"IBLPy/{cfg.version}"       
    
    def __init__(self, id: int):
        self.id = id
        self.logged_in = False 

    def login(self, api_token):
        """Logs in to the IBL API"""
        self.api_token = api_token
        self.logged_in = True
    
    async def request(
        self, 
        method: str, 
        endpoint: str,
        json: Optional[dict] = None, 
        headers: Optional[dict] = None, 
        auth: bool = False
    ):
        """Makes a API request"""
        headers = {} if not headers else headers
        
        if auth:
            if not self.logged_in:
                raise ValueError("Not logged in to IBL yet")
                
            headers["authorization"] = self.api_token
        
        headers["User-Agent"] = self.user_agent
        
        async with aiohttp.ClientSession() as sess:
            f = getattr(sess, method.lower())
            async with f(f"{cfg.api}{endpoint}", headers = headers, json = json) as res:
                if res.status == 429:
                    raise APIRatelimit()
           
                # Convert it to json
                i = 0
                json = await res.text()
                while isinstance(json, (bytes, str)) and i < 100:
                    json = json_lib.loads(json)
                    i+=1
            
                logger.debug(str(json))
            
                return APIResponse(res = res, json = json)
     
    
class BotHTTP(BaseHTTP):    
    async def set_stats(
        self,
        guild_count: int, 
        shard_count: Optional[int] = None
    ):        
        return await self.request(
            method="POST",
            endpoint=f"/bots/{self.id}/stats",
            json={
                "guild_count": guild_count,
                "shard_count": shard_count if shard_count else "0" # IBL API workaroud
            },
            auth=True
        )
   
    async def get_bot(self):
        api_res = await self.request(
            method="GET",
            endpoint=f"/bots/{self.id}",
        )
        
        if not api_res.success:
            return api_res
        
        return Bot(api_res.json)

    async def get_user_votes(self, user_id: int):
        api_res = await self.request(
            method="GET",
            endpoint=f"/users/{user_id}/bots/{self.id}/votes",
            auth=True
        )

        if not api_res.success:
            return api_res
        return UserVotes(api_res.json)

    
class UserHTTP(BaseHTTP):         
    async def get_user(self, debug: bool = False):
        api_res = await self.request(
            method="GET",
            endpoint=f"/users/{self.id}", 
        )

        if not api_res.success:
            return api_res
    
        return User(api_res.json)

