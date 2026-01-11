import os
import json
import datetime
import pandas as pd
import backoff
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from jsonc_parser.parser import JsoncParser

def get_google_services(token_path, creds_path, scopes):
    """
    Unified authentication for Google Sheets and Calendar.
    """
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    sheets_service = build('sheets', 'v4', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
    return sheets_service, calendar_service

def load_jsonc(path):
    """
    Helper for parsing JSONC files.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return JsoncParser.parse_file(path)

def fetch_calendar_events(service, calendar_id, time_min=None, time_max=None):
    """
    Fetches events from the specified Google Calendar.
    """
    if time_min is None:
        now = datetime.datetime.now(datetime.timezone.utc)
        time_min = (now - datetime.timedelta(days=30)).isoformat()
    
    if time_max is None:
        # Default to end of current year
        year = datetime.datetime.now().year
        time_max = datetime.datetime(year, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc).isoformat()

    events_result = service.events().list(
        calendarId=calendar_id, 
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

@backoff.on_exception(backoff.expo, HttpError, max_tries=5)
def create_calendar_event(service, calendar_id, event_body):
    """
    Inserts an event into Google Calendar with exponential backoff.
    """
    return service.events().insert(calendarId=calendar_id, body=event_body).execute()

def delete_events_from_csv(csv_path, service, calendar_id):
    """
    Delete events from the calendar based on a CSV file containing event IDs.
    """
    if not os.path.exists(csv_path):
        print(f"CSV not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    if 'ID' not in df.columns and 'id' not in df.columns:
        print("No 'ID' or 'id' column found in CSV.")
        return
    
    id_col = 'ID' if 'ID' in df.columns else 'id'
    
    print(f"Identified {len(df)} events for deletion.")
    confirm = input(f"Are you sure you want to delete {len(df)} events from calendar? (y/n): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return

    for event_id in df[id_col]:
        try:
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            print(f"Deleted event: {event_id}")
        except HttpError as e:
            if e.resp.status == 404:
                print(f"Event already deleted or not found: {event_id}")
            else:
                print(f"Error deleting {event_id}: {e}")
        except Exception as e:
            print(f"Error deleting {event_id}: {e}")
