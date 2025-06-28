from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Request from the frontend to the chat agent
class ChatRequest(BaseModel):
    message: str = Field(..., example="Book a call tomorrow at 3 PM")

# Response from the agent to the frontend
class ChatResponse(BaseModel):
    response: str

# Internal structure to hold user input and extracted metadata
class BookingIntent(BaseModel):
    raw_text: str
    intent: str                       # e.g., "check_availability", "book_meeting"
    date: Optional[str] = None       # ISO format date string
    time_start: Optional[str] = None # e.g., "15:00"
    time_end: Optional[str] = None   # e.g., "16:00"

# Slot model representing an available time
class TimeSlot(BaseModel):
    start: datetime
    end: datetime

# Response structure when showing available slots
class AvailabilityResponse(BaseModel):
    slots: List[TimeSlot]
    message: str
