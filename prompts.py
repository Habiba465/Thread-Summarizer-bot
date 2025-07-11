BASE_SYSTEM_PROMPT = """
You are a helpful assistant that summarizes Slack threads.
Be natural, concise, and cool, like a human colleague don't be overly formal.
The user will provide a command and the full thread context. Your task is to respond to the command based on the context.

The thread context should be enclosed in <THREAD> tags
"""

DEFAULT_SUMMARY_PROMPT = """
could you give me a summary of the following thread, explain it in your own words.
"""

BULLET_POINTS_PROMPT = """
could you give a summary of this thread, but can you please format it as a list of bullet points?
"""

ACTION_ITEMS_PROMPT = """
can you analyze this thread and tell me just the action items? I want to see who is responsible for what. If there are no clear action items, just say that.
"""

def create_question_prompt(question):
    return f"'{question}', Could you answer based on the context?"

