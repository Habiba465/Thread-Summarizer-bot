from dotenv import load_dotenv
import os
import re
# slack imports
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# the functions are organized into seprate files for easier devlopment
from ai_service import fetch_ai_response
from time_utils import parse_time_argument
from slack_utils import fetch_channel_history, fetch_formatted_thread
from parser import parse_command_text
import prompts

load_dotenv()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

def get_command_from_mention(text):
    """Removes the bot's mention from the text to just get the command."""
    return re.sub(r'<@U[A-Z0-9]+>\s*', '', text).strip()


@app.command("/summarize")
def handle_channel_summary(ack, body, client, say, logger):
    ack()
    
    channel_id = body['channel_id']
    user_command = body.get('text', 'last:24h') # Default is last 24h

    oldest_ts = parse_time_argument(user_command)

    if not oldest_ts:
        say(
            text="Sorry, I didn't get that time format. Try something like `last:24h`, `last:3d`, or `since:monday`.",
            response_type="ephemeral"
        )
        return

    initial_response = say(text=f"Hey! I'm summarizing this channel's activity from `{user_command}`")
    thread_ts_for_reply = initial_response['ts']
    
    try:
        channel_context = fetch_channel_history(client, channel_id, oldest_ts)

        if not channel_context or channel_context.strip() == "":
            say(
                text="I looked, but there for the given timeframe, I can't see any messages",
                thread_ts=thread_ts_for_reply
            )
            return

        summary = fetch_ai_response(
            system_prompt=prompts.BASE_SYSTEM_PROMPT,
            user_prompt=prompts.CHANNEL_SUMMARY_PROMPT,
            thread_context=channel_context
        )

        client.chat_update(
            channel=channel_id,
            ts=thread_ts_for_reply,
            text=f"*Here's a summary for `{user_command}`:*\n\n{summary}"
        )

    except Exception as e:
        logger.error(f"Error in /summarize command: {e}")
        client.chat_update(
            channel=channel_id,
            ts=thread_ts_for_reply,
            text=f"Yikes, something went wrong on my end. Sorry about that. `Error: {e}`"
        )





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

