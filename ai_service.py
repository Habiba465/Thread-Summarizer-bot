import requests
import json

AI_API_URL = "https://ai.hackclub.com/chat/completions"

def fetch_ai_response(system_prompt, user_prompt, thread_context):
    headers = {"Content-Type": "application/json"}
    
    full_user_content = f"{user_prompt}\n<THREAD>\n{thread_context}\n</THREAD>"
    
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_content}
        ]
    }

    try:
        response = requests.post(AI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        data = response.json()
        return data['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        print(f"Error calling AI API: {e}")
        return "Sorry, I had trouble connecting to the AI. Maybe try again in a bit?"

    except (KeyError, IndexError) as e:
        print(f"Error parsing AI response: {e}")
        return "Sorry, the AI gave a weird response. Couldn't figure it out."