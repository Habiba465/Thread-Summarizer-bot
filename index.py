import requests
import json
from dotenv import load_dotenv
import os

# slack necssary imports, using socket mode for development only
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()
# main app for slack bot
bot_token = os.getenv("SLACK_BOT_TOKEN")
app_token = os.getenv("SLACK_APP_TOKEN")

app = App(token=bot_token)

SYSTEM_PROMPT = """
You will get the full thread from slack, your task is to summarize it all in a concise way
Also explain it in your way and don't write overly polish respones and be natural just as a human would do 
remeber be cool!
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


@app.event("app_mention")
def handle_app_mention(event, say, client):
    
    if 'thread_ts' in event:

        channel_id = event['channel']
        thread_ts = event['thread_ts']

        try:
            say(text="Got it! I am reading this thread, a summary will appear soon", thread_ts=thread_ts)

            result = client.conversations_replies(channel=channel_id, ts=thread_ts)
            messages = result.get('messages', [])

            if not messages:
                say(text="I couldn't find any messages in this thread to summarize.", thread_ts=thread_ts)
                return

            formatted_thread = []
            user_cache = {}
            for msg in messages:
                user_id = msg.get('user')
                if user_id not in user_cache:
                    try:
                        user_info = client.users_info(user=user_id)
                        user_cache[user_id] = user_info['user']['real_name']
                    except Exception:
                        user_cache[user_id] = "An unknown user"
                
                user_name = user_cache[user_id]
                text = msg['text']
                text = text.replace(f"<@{event['user']}>", "").strip()
                if text: 
                    formatted_thread.append(f"{user_name}: {text}")
            
            thread_text_to_summarize = "\n".join(formatted_thread)

            if not thread_text_to_summarize:
                say(text="Looks like this thread is empty or only contains my mention. there's nothing to summarize", thread_ts=thread_ts)
                return

            summary = get_ai_summary(thread_text_to_summarize)

            say(text=f"*Here's a summary of this thread:*\n\n{summary}", thread_ts=thread_ts)

        except Exception as e:
            print(f"Error handling mention in thread: {e}")
            say(
                text=f"Oops, something went wrong while processing the summary. `Error: {e}`",
                thread_ts=thread_ts
            )
    else:
        say(
            text="Hello! to summarize a thread, please mention me (`@ThreadSummarizer`) in a thread"
        )

if __name__ == "__main__":
    print("I am running!")
    handler = SocketModeHandler(app, app_token=app_token)
    handler.start()

