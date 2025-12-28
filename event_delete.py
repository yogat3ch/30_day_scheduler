import os
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
CALENDAR_ID = 'primary'
CREATED_EVENTS_CSV = 'created_events.csv'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def main():
    if not os.path.exists(CREATED_EVENTS_CSV):
        print(f"Error: {CREATED_EVENTS_CSV} not found. Run the sync script first.")
        return

    df = pd.read_csv(CREATED_EVENTS_CSV)
    if 'ID' not in df.columns:
        print(f"Error: CSV does not have 'ID' column.")
        return

    service = get_calendar_service()
    
    print(f"Starting deletion of {len(df)} events...")
    
    deleted_count = 0
    for _, row in df.iterrows():
        event_id = row['ID']
        summary = row.get('Summary', 'No Summary')
        try:
            service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
            print(f"Deleted: {summary} ({event_id})")
            deleted_count += 1
        except HttpError as error:
            if error.resp.status == 404:
                print(f"Event already deleted or not found: {summary}")
            else:
                print(f"Failed to delete {summary}: {error}")

    print(f"\nFinished. Deleted {deleted_count} events.")
    
    # Optionally remove the CSV after deletion
    os.remove(CREATED_EVENTS_CSV)
    print(f"Removed {CREATED_EVENTS_CSV}")

if __name__ == '__main__':
    main()
