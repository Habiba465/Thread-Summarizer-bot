import re

# This is for parsing the slash commands
def parse_command_text(text):
    text = text.strip()

    if not text:
        return "default", None

    style_match = re.search(r"style:(\w+)", text)
    if style_match:
        style = style_match.group(1).lower()
        if style in ["bulletpoints", "actionitems"]:
            return "style", style
    question_match = re.search(r'question:"([^"]+)"', text)
    if question_match:
        question = question_match.group(1)
        return "question", question

    return "default", None
