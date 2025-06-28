from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
from dateutil import parser

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Make sure this file is in your root project folder

# --------------------------------------
# Helper: Authenticate and get calendar service
# --------------------------------------
def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('calendar', 'v3', credentials=credentials)

# --------------------------------------
# Feature 1: Book a meeting event
# --------------------------------------
def book_event(start_time: datetime, end_time: datetime, summary="Meeting with AI Assistant"):
    service = get_calendar_service()
    calendar_id = 'primary'

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Asia/Kolkata'
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Asia/Kolkata'
        },
    }

    created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
    return created_event

# --------------------------------------
# Feature 2: Check free/busy slots
# --------------------------------------
def get_free_slots(start_date: datetime, end_date: datetime):
    service = get_calendar_service()
    calendar_id = 'primary'

    response = service.freebusy().query(
        body={
            "timeMin": start_date.isoformat(),
            "timeMax": end_date.isoformat(),
            "timeZone": "Asia/Kolkata",
            "items": [{"id": calendar_id}]
        }
    ).execute()

    busy_times = response['calendars'][calendar_id].get('busy', [])
    return busy_times

# --------------------------------------
# Feature 3: List upcoming meetings
# --------------------------------------
def list_upcoming_events(n=5):
    service = get_calendar_service()
    now = datetime.utcnow().isoformat() + "Z"

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=n,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        return "📭 You have no upcoming events."

    response = "📅 Upcoming events:\n"
    for event in events:
        summary = event.get("summary", "No Title")
        start_raw = event['start'].get('dateTime', event['start'].get('date'))
        start_time = parser.parse(start_raw).astimezone(pytz.timezone("Asia/Kolkata"))
        start_str = start_time.strftime('%I:%M %p, %A %d %B %Y')
        response += f"- {summary} at {start_str}\n"
    return response

def find_free_windows(start_date: datetime, end_date: datetime, slot_minutes=30):
    print(f"[DEBUG] start_date={start_date}, end_date={end_date}")
    try:
        busy_slots = get_free_slots(start_date, end_date)
    except Exception as e:
        print("[ERROR] Failed to get busy slots:", str(e))
        return "❌ Error checking availability. Please try again."

    tz = pytz.timezone("Asia/Kolkata")

    # Build all possible time slots
    free_slots = []
    current = start_date
    while current + timedelta(minutes=slot_minutes) <= end_date:
        overlap = False
        for busy in busy_slots:
            busy_start = parser.parse(busy['start']).astimezone(tz)
            busy_end = parser.parse(busy['end']).astimezone(tz)
            if current < busy_end and current + timedelta(minutes=slot_minutes) > busy_start:
                overlap = True
                break
        if not overlap:
            slot_start = current.strftime('%I:%M %p')
            slot_end = (current + timedelta(minutes=slot_minutes)).strftime('%I:%M %p')
            free_slots.append(f"{slot_start} - {slot_end}")
        current += timedelta(minutes=slot_minutes)

    if not free_slots:
        return "❌ Sorry, you have no free slots in the selected time range."

    return "🕐 You're available at:\n" + "\n".join(f"- {slot}" for slot in free_slots)

# --------------------------------------
# Feature 4: Cancel a meeting by time
# --------------------------------------
def cancel_event(target_time: datetime, calendar_id='primary'):
    service = get_calendar_service()

    # ⏰ Ensure timezone-aware datetime
    if target_time.tzinfo is None:
        target_time = pytz.timezone("Asia/Kolkata").localize(target_time)

    now = datetime.utcnow().isoformat() + 'Z'

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    if not events:
        return "📭 No upcoming events to cancel."

    for event in events:
        start_raw = event['start'].get('dateTime', event['start'].get('date'))
        event_start = parser.parse(start_raw).astimezone(pytz.timezone("Asia/Kolkata"))

        # ⏱️ Match within 15 min of target
        delta = abs((event_start - target_time).total_seconds())
        if delta <= 15 * 60:
            service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
            start_str = event_start.strftime('%I:%M %p, %A %d %B %Y')
            return f"🗑️ Meeting at {start_str} has been cancelled."

    return "⚠️ No matching meeting found to cancel."
