
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


def fetch_channel_history(client, channel_id, oldest_ts):
    """
    This fetches up to 100 of the most recent messages from a channel's main feed,
    and it ignores any messages that are part of a thread.
    """
    try:
        result = client.conversations_history(
            channel=channel_id,
            oldest=oldest_ts,
            limit=100,
            inclusive=True
        )
        messages = result.get('messages', [])
        
        if not messages:
            return None

        user_cache = {}
        formatted_messages = []

        for msg in messages:
            if 'thread_ts' in msg and msg.get('ts') != msg.get('thread_ts'):
                continue # Skip messages that are replies in a thread

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
        
        # Slack returns messages from newest to oldest, so we will reverse them
        return "\n".join(reversed(formatted_messages))

    except Exception as e:
        print(f"Error fetching channel history: {e}")
        return None



