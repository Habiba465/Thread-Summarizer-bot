import requests

from dotenv import load_dotenv
import os

# slack necssary imports, using socket mode for development only
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()
# main app for slack bot
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

SYSTEM_PROMPT = """
You will get the full thread from slack, your task is to summarize it all in a concise way
Also explain it in your way and don't write overly polish respones and be natural just as a human would do 

<THREAD>
"""

def get_ai_summary(text_to_summarize):
    """send the thread text to the ai.hackclub.com and returns the full summary"""
    url = "https://ai.hackclub.com/chat/completions"
    headers = {"Content-Type": "application/json"}
        
    payload = {
        "messages": [
            {"role": "user", "content": SYSTEM_PROMPT+text_to_summarize+ "</THREAD>"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        data = response.json()
        summary = data['choices'][0]['message']['content']
        return summary

    except requests.exceptions.RequestException as e:
        print(f"Error calling AI API: {e}")
        return "Sorry, something went wrong, try again later."

    except (KeyError, IndexError) as e:
        print(f"Error parsing AI response: {e}")
        return "Sorry, something went wrong, try again later."

if __name__ == "__main__":
    print("I am running!")
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()

