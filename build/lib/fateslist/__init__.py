api_modes = []
try:
    import aiohttp
    api_modes.append("async")
except Exception:
    raise ImportError("You must have aiohttp installed to import this library!")
    
try:
    import uvicorn
    import fastapi
    api_modes.append("webhook")
except:
    uvicorn = None
    fastapi = None

import discord

from fateslist.main import *
from fateslist.config import *
from fateslist.ws import *
from fateslist.utils import *
from fateslist.system import *

__version__ = version
