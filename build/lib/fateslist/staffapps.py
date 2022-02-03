from .http import BaseHTTP
from .classes import StaffAppQuestions
from typing import Optional

class StaffAppClient(BaseHTTP):
    """
        Initialize a fateslist.py Staff App Client. You can use this to get user stats!
            
        :param user_id: The User ID you wish to use with the Fates List API. Required for creating a staff app

        :param api_token: The API Token of the bot. You can find this by clicking API Token under the "About Section". 
            This is optional however you will not be able to create staff apps if you do not pass a API Token
    """
    def __init__(self, user_id: int = None, api_token: Optional[str] = ""):
        self.user_id = user_id
        self.id = user_id
        if api_token:
            self.login(api_token)
    
    async def get_questions(self):
        """
            Gets the list of questions from the API
            
            :return: A list of questions
        """
        api_res = await self.request(
            method="GET",
            endpoint="/staff-apps/questions",
        )
        
        if not api_res.success:
            return api_res
        
        return StaffAppQuestions(**api_res.json)
    
    async def post_staff_app(self, responses: dict):
        """
            Posts the staff app to the API
            
            :param responses: A dictionary of responses
            
            :return: A APIResponse object
        """
        api_res = await self.request(
            method="POST",
            endpoint=f"/staff-apps/{self.id}",
            json={"answers": responses},
            auth=True,
        )
        
        return api_res