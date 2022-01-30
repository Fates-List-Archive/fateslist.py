import fateslist.config as cfg
import fateslist.http as _http
from fateslist.classes import InvalidMode, APIResponse
from fateslist import api_modes, fastapi, uvicorn, ws, discord
from loguru import logger
from typing import Optional, Awaitable
import os
import asyncio
import time

class BotClient():
    """
        Initialize a Fates List Bot Client. You can use this to get/post bot stats, fetch a bot etc. etc.!
            
        :param bot_id: The Bot ID you wish to use with the Fates List API

        :param api_token: The API Token of the bot. You can find this by clicking API Token under the "About Section". 
            This is optional however you will not be able to post stats if you do not pass a API Token
    """

    def __init__(self, bot_id: int, api_token: Optional[str] = ""):
        self.bot_id = bot_id
        self.http = _http.BotHTTP(bot_id)
        
        if api_token:
            self.http.login(api_token)

            
    async def set_stats(self, guild_count: int, shard_count: Optional[int] = None) -> APIResponse:
        """
            Posts bot stats to the Fates List API. This is optional but it is recommended to post stats to the API.
            
            :param guild_count: Amount of servers your bot is in

            :param shard_count: Amount of shards your bot is in. This is optional

            :return: This will always be returned unless something goes wrong, in which case you will get an exception
            :rtype: APIResponse 
        """
        return await self.http.set_stats(guild_count, shard_count)
  
    
    async def get_bot(self):
        """
            Asynchronously get a bot. This does not take any parameters.

            :return: If the bot was not found or if fateslist.py could not parse the JSON request for any reason
            :rtype: None

            :return: This will be returned on an error
            :rtype: APIResponse

            :return: This will be returned on an error
            :rtype: APIRatelimit

            :return: This is the bot object returned from the API
            :rtype: Bot
        """
        return await self.http.get_bot()

    async def get_user_votes(self, user_id: int):
        """
            This returns whether or not a user has voted

            :return: This will be returned if you are ratelimited
            :rtype: APIResponse

            :return: Whether or not the user has voted or not
            :rtype: UserVotes
        """
        return await self.http.get_user_votes(user_id)

class UserClient():
    """
        Initialize a fateslist.py User Client. You can use this to get user stats!
            
        :param user_id: The User ID you wish to use with the Fates List API
    """
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.http = _http.UserHTTP(user_id)

    async def get_user(self):
        """
            Get a user. This does not take any parameters.

            :return: If the user was not found or if fateslist could not parse the JSON request for any reason
            :rtype: None

            :return: This will be returned if you are ratelimited
            :rtype: APIResponse

            :return: This is the user object returned from the API
            :rtype: User
        """
        return await self.http.get_user()


async def _default_get_counts(ap):
    """Returns guild and shard count for default autoposter"""
    return {
        "guild_count": len(ap.discli.guilds),
        "shard_count": len(ap.discli.shards) if ap.sharding else None
    }
    
class AutoPoster():
    """
        This is Fates List Auto Poster. It will post stats for you on an interval you decide
            and it will then run a function of your choice (if requested) after posting each time.

        You can stop a Auto Poster by calling the ``stop`` function.
        
        :param get_counts: A async function that takes in the AutoPoster object and then
            returns the dict {"guild_count: guild count, "shard_count": shard_count} for the autoposter.
            A default value for this is provided for ease of use

        :param interval: How long to wait each time you post. It is required to use at least 5 minutes which is 300 seconds.
            Specifying a value below 300 seconds will set the interval to 300 seconds anyways

        :param botcli: The fateslist.py BotClient of the bot you want to post stats for. 
            It must have the API token set either during initialization or afterwards by setting the api_token parameter

        :param discli: The discord.Client (or like interfaces like discord.Bot/discord.AutoShardedBot) of the bot you want to post stats for.
            If you wish to add shard counts, please give a discord.AutoShardedClient and pass sharding = True or use get_counts

        :param on_post: The function to call after posting. Set to None if you don't want this.
            This function needs to accept three arguments, the guild count sent, the shard count set 
            and the response (which will either be a APIResponse, a APIRatelimit or None). 
            Shard count will be None if sharding is disabled and/or get_count provided doesn't support it

        :param sharding: Whether we should post sharding as well. Requires a discord.AutoShardedClient
    """
    def __init__(
        self, 
        interval: int,
        botcli: BotClient, 
        discli: discord.Client, 
        sharding = None, 
        on_post = None,
        get_counts: Awaitable = _default_get_counts,
    ):

        if interval > 300:
            self.interval = interval
        else:
            self.interval = 300
        self.get_counts = get_counts
        self.botcli = botcli
        self.discli = discli
        self.on_post = on_post
        self.sharding = sharding
        self.keep_running = True
        self.task = None

    async def autoposter(self):
        """This is the autoposting function that is run by the ``start`` function here (using asyncio.create_task)"""
        while True:
            if not self.keep_running:
                self.keep_running = True
                logger.info("fateslist.py: AutoPoster has exited successfully!")
                return

            if self.interval < 300:
                self.interval = 300

            try:
                
                try:
                    counts = await self.get_counts(self)
                except Exception as exc:
                    logger.warning("Using self in get_counts did not work, trying no args...")
                    counts = await self.get_counts()
                    
                res = await self.botcli.set_stats(counts["guild_count"], counts["shard_count"])
                if self.on_post:
                    await self.on_post(counts["guild_count"], counts["shard_count"], res)
                logger.success(f"fateslist.py: Stats posted successfully at {time.time()}")
            except Exception as ex:
                logger.error(f"fateslist.py: Could not post stats because: {ex}")
            await asyncio.sleep(self.interval)

    def start(self):
        """Starts the auto poster using asyncio.create_task and returns the created task. This must be done in the on_ready function in discord.py"""
        self.task = asyncio.create_task(self.autoposter())
        return self.task

    def stop(self):
        """
            Stops the auto poster by setting the ``keep_running`` attribute to False. Since the exact name may change, it is recommended to use ``stop`` instead of manually setting the attribute.

            The autoposter will only stopped after the interval specified

            This will return the autoposter asyncio task
        """
        self.keep_running = False
        print("fateslist.py: AutoPoster is stopping... Waiting for it to next wake up to post stats")
        return self.task

class Webhook():
    """
        This is an fateslist.py webhook. It takes a BotClient, your webhook secret and the awaitable/asyncio corouting to call after getting a vote. To start your webhook:

            Use start_ws_task if you are running this in discord.py. make sure you start the webhook in your on_ready event (at the very end of it since it's blocking)

            Use start_ws_normal if you are running this seperately from discord.py. It will be run using asyncio.run instead of asyncio.create_task

            Use the start_ws coroutine if you want to run the webhook yourself using asyncio

            Use create_app if you want to get the FastAPI ASGI app and deploy the webhook using your own server. Uvicorn still needs to be installed even if you use a different ASGI server
    """
    def __init__(self, botcli: BotClient, coro: object, secret: str = None):
        if "webhook" not in api_modes:
            raise InvalidMode("fastapi")
        self.botcli = botcli
        self.secret = secret
        self.coro = coro

    def start_ws_task(self, route, port = 8012):
        """
            Start webhook using asyncio.create_task (discord.py). Use this in a discord.py on_ready event (at the very end of it since it's blocking).
        """
        asyncio.create_task(self.start_ws(route, port = port))

    def start_ws_normal(self, route, port = 8012):
        """
            Start webhook using asyncio.run for normal non-discord.py usecases
        """
        asyncio.run(self.start_ws(route, port = port))

    def create_app(self, route):
        """Creates a FastAPI ASGI app and returns it so you can deploy it how you want to deploy it"""
        ws.wh_func = self.coro
        ws.botcli = self.botcli
        ws.secret = self.secret
        app = fastapi.FastAPI(docs_url = None, redoc_url = None)
        app.include_router(
            router = ws.router,
            prefix=route,
        )
        return app

    async def start_ws(self, route, port = 8012):
        """
            Coroutine to start webhook using any asyncio method you want.
        """
        server = uvicorn.Server(uvicorn.Config(self.create_app(route), host = "0.0.0.0", port = port))
        await server.serve()
        try:
            os._exit()
        except:
            os._exit(0)
