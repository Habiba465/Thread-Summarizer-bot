import re
from datetime import datetime, timedelta

def parse_time_argument(text):
    """
    this parses a text command (e.g "last:24h", "since:monday") 
    returns a timestamp for the start time and none if invalid 
    """
    text = text.strip().lower()
    now = datetime.now()

    # handles "last:Xh/d" (e.g last:24h, last:7d)
    last_match = re.match(r"last:(\d+)([hd])", text)
    if last_match:
        value = int(last_match.group(1))
        unit = last_match.group(2)
        if unit == 'h':
            delta = timedelta(hours=value)
        elif unit == 'd':
            delta = timedelta(days=value)
        return (now - delta).timestamp()

    # handles "since:weekday" (e.g., since:monday)
    since_match = re.match(r"since:(\w+)", text)
    if since_match:
        day_name = since_match.group(1)
        days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        
        try:
            target_day_index = days_of_week.index(day_name)
        except ValueError:
            return None 

        days_ago = (now.weekday() - target_day_index + 7) % 7
        if days_ago == 0: # if today is the target day, get from last week
            days_ago = 7
        
        target_date = now - timedelta(days=days_ago)
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        return start_of_day.timestamp()
    
    return None
