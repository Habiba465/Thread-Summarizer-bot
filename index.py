from dotenv import load_dotenv
import os
import re
# slack imports
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# the functions are organized into seprate files for easier devlopment
from ai_service import fetch_ai_response
from parser import parse_command_text
import prompts

load_dotenv()


app = App(token=os.getenv("SLACK_BOT_TOKEN"))

def fetch_formatted_thread(client, channel_id, thread_ts):
    try:
        result = client.conversations_replies(channel=channel_id, ts=thread_ts)
        messages = result.get('messages', [])
        
        if not messages:
            return None

        user_cache = {}
        formatted_messages = []

        for msg in messages:
            user_id = msg.get('user')
            if user_id not in user_cache:
                try:
                    user_info = client.users_info(user=user_id)
                    user_cache[user_id] = user_info['user']['real_name']
                except Exception:
                    user_cache[user_id] = "An unknown user"
            
            user_name = user_cache[user_id]
            text = msg.get('text', '').strip()

            if text:
                formatted_messages.append(f"{user_name}: {text}")
        
        return "\n".join(formatted_messages)

    except Exception as e:
        print(f"Error fetching thread: {e}")
        return None

def get_command_from_mention(text):
    """Removes the bot's mention from the text to just get the command."""
    return re.sub(r'<@U[A-Z0-9]+>\s*', '', text).strip()



@app.event("app_mention")
def handle_app_mention(event, say, client, logger):
    thread_ts = event.get('thread_ts')
    channel_id = event['channel']


    if not thread_ts:
        say(
            text="Hey! I work only in threads till now (open a thread and try again).",
            ephemeral=True
        )
        return

    try:
        say(text="Got it! reading the thread now, one sec", thread_ts=thread_ts)

        thread_context = fetch_formatted_thread(client, channel_id, thread_ts)

        if not thread_context:
            say(text="Looks like this thread is empty", thread_ts=thread_ts)
            return

        user_command = get_command_from_mention(event['text'])
        command_type, value = parse_command_text(user_command)

        if command_type == 'style' and value == 'bulletpoints':
            user_prompt = prompts.BULLET_POINTS_PROMPT
        elif command_type == 'style' and value == 'actionitems':
            user_prompt = prompts.ACTION_ITEMS_PROMPT
        elif command_type == 'question':
            user_prompt = prompts.create_question_prompt(value)
        else:
            user_prompt = prompts.DEFAULT_SUMMARY_PROMPT
        
        summary = fetch_ai_response(
            system_prompt=prompts.BASE_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            thread_context=thread_context
        )
        
        say(text=f"*Here's the summary:*\n\n{summary}", thread_ts=thread_ts)

    except Exception as e:
        logger.error(f"Error in /summarize command: {e}")
        say(
            text=f"Yikes, something went wrong. Sorry about that. `Error: {e}`",
            thread_ts=thread_ts
        )


@app.event("app_mention")
def handle_app_mention(event, say):
    if 'thread_ts' not in event:
        say(
            text="Hey! To get a summary, go into a thread and use the `/summarize` command."
        )


if __name__ == "__main__":
    print("I am running!")
    app_token = os.getenv("SLACK_APP_TOKEN")
    handler = SocketModeHandler(app, app_token=app_token)
    handler.start()

