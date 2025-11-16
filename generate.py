import os
import json
from typing import Any, Dict


from dotenv import load_dotenv
from google import genai
from google.genai import types

SYSTEM_PROMPT = """
You are a usefull AI Agent, used for creating football (soccer) match caption,
for interesting match events. The captions generated should not be longer than
3 sentences.
"""

def generate_caption(msg: Dict[str, Any]) -> str:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    eventType = f"{msg.get('type','')}\n"
    comment = f"comment: {msg.get('comment','')}\n"
    eventTime = f"time: {msg.get('time','')}\n"

    playerRef1 = msg.get("playerRef1", "")
    teamRef1 = msg.get("teamRef1", "")
    playerRef2 = msg.get("playerRef2", "")
    teamRef2 = msg.get("teamRef2", "")

    # Load squads
    with open("data/celtic-squad.json") as f:
        squad = json.load(f)["squad"][0]
        for p in squad["person"]:
            if p["id"] == playerRef1:
                playerRef1 = f"player-1: {p['firstName']} {p['lastName']}\n"
        if teamRef1:
            teamRef1 = f"team-1: {squad['contestantName']}\n"

    with open("data/kilmarnock-squad.json") as f:
        squad = json.load(f)["squad"][0]
        for p in squad["person"]:
            if p["id"] == playerRef2:
                playerRef2 = f"player-2: {p['firstName']} {p['lastName']}\n"
        if teamRef2:
            teamRef2 = f"team-2: {squad['contestantName']}\n"

    caption = (
        eventType + comment + eventTime + playerRef1 + teamRef1 + playerRef2 + teamRef2
    )

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=caption,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
        ),
    )

    if response.text:
        return response.text 
    return ""
