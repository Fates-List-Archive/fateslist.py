import aiohttp

async def blstats():
    """
    Returns bot list stats
    """
    async with aiohttp.ClientSession() as sess:
        async with sess.get(f"https://api.fateslist.xyz/api/blstats?workers=true") as res:
            return res