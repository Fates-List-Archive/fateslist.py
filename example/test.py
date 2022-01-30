import sys
sys.path.append(".")
import fateslist, asyncio, discord
from testcfg import TOKEN

async def got_vote(vote, secret):
    print("Got vote:", vote, "with secret:", secret)

async def test_poster(gc, sc, res):
    print(gc, sc, res)

fl = fateslist.BotClient(
    bot_id = 731594086775128104,
    api_token="U7zk7bvz9cTAhcffPGL4JURmSMwBVkl5mZpue33gxYQ8gOIiwnfXOaPF4kU8KxttWyZaMNOD8ZgTyCw8RtYS5dXwtyTGQzkmFBfiIK5FCTHUZMyAZOa5fXFkyYNrHkqZU83m"
)
client = discord.AutoShardedClient()

@client.event
async def on_message(msg):
    print(msg)

@client.event
async def on_ready():
    print(f"Ready! {client.user}")
    print("Has Rootspring voted?")
    r = await fl.get_user_votes(563808552288780322)
    #print(r)
    print("Rootsprings user info")
    r = await fateslist.UserClient(563808552288780322).get_user()
    #print(r)
    r = await fl.get_bot()
    print(r.guild_count, r.shard_count, r.website)
    a = fateslist.Webhook(botcli = fl, secret = "MY_SECRET", coro = got_vote)
    ap = fateslist.AutoPoster(interval = 300, botcli = fl, discli = client, on_post = test_poster, sharding = True)
    ap.start()
    a.start_ws_task(route = "/fl", port = 8016)

client.run(TOKEN)
