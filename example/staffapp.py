"""A simple example of using fateslist.py to create a staff application"""
from fateslist.classes import APIResponse
from fateslist.staffapps import StaffAppClient
import asyncio

id = input("User ID? ")
token = input("Token? ")

sc = StaffAppClient(user_id=int(id), api_token=token)

async def main():
    questions = await sc.get_questions()
    if isinstance(questions, APIResponse):
        print("Error:", questions.reason)
        return
    
    responses = {}

    i = 1
    for q in questions.questions:
        print(f"\nQuestion {i} of {len(questions.questions)}")
        responses[q.id] = input(f"ID: {q.id} - {q.question} - ({q.minlength} - {q.maxlength} chars) > ")
        i += 1

    print("Posting staff application")
    post = await sc.post_staff_app(responses)
    print(f"Got response: {post}")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())