"""
Google Calendar interaction module — checks availability and books events.
Now includes error handling for missing credentials, malformed datetimes, and API errors.
"""

import os
import logging
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'app/credentials.json'
TIMEZONE = 'Asia/Kolkata'

try:
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('calendar', 'v3', credentials=creds)
except Exception as e:
    service = None
    logger.error("❌ Failed to load Google Calendar credentials: %s", e)

def check_availability(start_time_str, end_time_str, timezone='Asia/Kolkata'):
    """
    Checks if the given slot is available (no overlaps with existing events).
    Returns True if available, False if busy or API errors occur.
    """
    # Sends a free/busy query to Google Calendar to determine whether the requested time slot
    # is available. Returns True if the time is free, False if there's a conflict or error.
    if not service:
        logger.warning("⛔ Calendar service not initialized.")
        return False

    try:
        # Verify that times are valid ISO 8601
        datetime.fromisoformat(start_time_str)
        datetime.fromisoformat(end_time_str)

        body = {
            "timeMin": start_time_str,
            "timeMax": end_time_str,
            "timeZone": timezone,
            "items": [{"id": "primary"}]
        }

        response = service.freebusy().query(body=body).execute()
        busy_times = response['calendars']['primary'].get('busy', [])
        return not busy_times

    except (ValueError, HttpError) as e:
        logger.error("⚠️ Availability check failed: %s", e)
        return False
    

def book_slot(start_time_str, duration_minutes=60, timezone='Asia/Kolkata'):
    """
    Books a meeting at the given ISO 8601 datetime.
    Returns success or error message.
    """
    # Attempts to book a calendar event using the Google Calendar API based on a validated
    # start time and duration. Returns a success message or an appropriate error description.
    try:
        start = datetime.fromisoformat(start_time_str)
        end = start + timedelta(minutes=duration_minutes)

        if not check_availability(start.isoformat(), end.isoformat(), timezone):
          return "❌ That time is not available."

        event = {
            'summary': 'Scheduled Appointment',
            'start': {'dateTime': start.isoformat(), 'timeZone': timezone},
            'end': {'dateTime': end.isoformat(), 'timeZone': timezone}
        }

        service.events().insert(calendarId='primary', body=event).execute()
        return f"✅ Booked from {start.strftime('%I:%M %p')} to {end.strftime('%I:%M %p')}."
    except Exception as e:
        logger.error("🚫 Failed to book slot: %s", e)
        return "⚠️ Something went wrong while booking. Please try again."
    