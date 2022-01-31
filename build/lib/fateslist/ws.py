import uuid
from fastapi import APIRouter, Header, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
from typing import Optional, Union
import secrets

router = APIRouter()

def abort(code: int) -> StarletteHTTPException:
    raise StarletteHTTPException(status_code=code)

def secure_strcmp(val1, val2):
    """
    From Django:

    Return True if the two strings are equal, False otherwise. This is a secure function
    """
    return secrets.compare_digest(val1, val2)


class VoteContext(BaseModel):
    """
        Represents a fateslist vote context. fateslist.py will make this a Vote class
    """
    user: str
    votes: int
    test: Optional[bool] = False

class Event(BaseModel):
    """Represents a event on fateslist"""
    e: int
    eid: uuid.UUID
    t: int
    ts: float
    user: str

class VoteModel(BaseModel):
    """The vote information itself"""
    ctx: VoteContext
    id: str
    m: Event

class Vote():
    """
        Represents a vote on IBL

        :param bot_id: The Bot ID of the vote

        :param user_id: The ID of the user who voted for your bot. In test mode, this will be 0

        :param username: The username who voted for your bot

        :param count: The amount of votes your bot now has

        :param test: Whether this is a test webhook or not

        :param timestamp: The timestamp (epoch) when the vote happened
    """
    def __init__(self, bot_id: int, user_id: int, test: bool, timestamp: int, count: int, username: str):
        self.bot_id = bot_id
        self.user_id = user_id
        self.test = test
        self.timestamp = timestamp

        if count.isdigit():
            self.count = int(count)
        else:
            self.count = 0

@router.post("/_dbg")
async def debug_webhook(request: Request):
    print((await request.body()), secret)

@router.post("/")
async def iblpy_webhook(vote: VoteModel, Authorization: str = Header("INVALID_SECRET")):
    if secret is None or secure_strcmp(secret, Authorization):
        pass
    else:
        return abort(401)

    return await wh_func(vote, secret)