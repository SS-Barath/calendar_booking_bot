import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import re
import pytz
import dateparser

from backend.calendar_utils import (
    book_event,
    list_upcoming_events,
    find_free_windows,
    cancel_event,
)
from langchain_community.chat_models import ChatOpenAI

# Load .env values
load_dotenv()

# Initialize the chat model
llm = ChatOpenAI(temperature=0)

# ----------------------------------------
# Extract and parse natural language datetime
# ----------------------------------------
def parse_datetime(user_input: str):
    """
    Uses regex to extract and dateparser to parse natural language datetime strings.
    """
    match = re.search(
        r'(tomorrow(?:\s+at\s+\d{1,2}(?::\d{2})?\s*(AM|PM)?)?|'
        r'today(?:\s+at\s+\d{1,2}(?::\d{2})?\s*(AM|PM)?)?|'
        r'next\s+\w+\s+at\s+\d{1,2}(?::\d{2})?\s*(AM|PM)?|'
        r'\d{1,2}(?::\d{2})?\s*(AM|PM)?)',
        user_input,
        re.IGNORECASE
    )
    if match:
        return dateparser.parse(match.group())
    return None

# ----------------------------------------
# Main Handler
# ----------------------------------------
def handle_booking(user_message: str):
    msg = user_message.lower()

    # Greeting
    if any(greet in msg for greet in ["hi", "hello", "hey", "how are you"]):
        return "👋 Hello! I can help you book, cancel, or list your calendar events."

    # Show upcoming meetings
    if any(q in msg for q in ["what meetings", "what's on", "show my events", "list calendar", "upcoming events"]):
        return list_upcoming_events()

    # Check availability
    if "free" in msg or "available" in msg:
        today = datetime.now(pytz.timezone("Asia/Kolkata"))
        start = today.replace(hour=9, minute=0, second=0, microsecond=0)
        end = today.replace(hour=18, minute=0, second=0, microsecond=0)

        if "tomorrow" in msg:
            start += timedelta(days=1)
            end += timedelta(days=1)

        try:
            return find_free_windows(start, end)
        except Exception as e:
            return f"❌ Error checking availability. Please try again.\nDetails: {str(e)}"

    # Cancel meeting
    if "cancel" in msg or "delete" in msg or "remove" in msg:
        parsed_time = parse_datetime(user_message)
        if not parsed_time:
            return "❌ Please specify when the meeting is, like 'Cancel my 3 PM meeting today'."
        try:
            return cancel_event(parsed_time)
        except Exception as e:
            return f"❌ Failed to cancel meeting: {str(e)}"

    # Book meeting
    parsed_time = parse_datetime(user_message)
    if not parsed_time:
        return "Sorry, I couldn't understand the date/time. Try something like 'Book a meeting tomorrow at 3 PM'."

    start = parsed_time
    end = start + timedelta(minutes=30)

    try:
        event = book_event(start, end)
        return f"✅ Meeting booked from {start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')} on {start.strftime('%A, %d %B %Y')}."
    except Exception as e:
        return f"⚠️ Failed to book meeting: {str(e)}"
