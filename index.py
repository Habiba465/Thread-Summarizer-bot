# requests for ai.hackclub.com
import requests

# for loading env 
from dotenv import load_dotenv
import os

# slack necssary imports
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


# main app for slack bot
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# just for testing will remove it later
@app.event("app_mention")
def handle_app_mention_events(body, say):
    say("yay, i am working!")


# this function will take the thread then return a summary
def ai_summary(text_to_summarize):
    pass

if __name__ == "__main__":
    print("I am running!")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()