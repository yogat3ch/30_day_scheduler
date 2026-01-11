import os
import pandas as pd
import datetime
from utils_calendar_general import fetch_calendar_events

def update_created_events_csv(calendar_service, calendar_id, csv_path):
    """
    Fetches events from Google Calendar and updates the local CSV store.
    """
    print(f"Syncing {csv_path} with Google Calendar...")
    calendar_events = fetch_calendar_events(calendar_service, calendar_id)
    
    records = []
    for event in calendar_events:
        start = event['start'].get('dateTime') or event['start'].get('date')
        records.append({
            'Summary': event.get('summary'),
            'ID': event.get('id'),
            'Begin': start
        })
    
    df_sync = pd.DataFrame(records)
    df_sync.to_csv(csv_path, index=False)
    print(f"Successfully synced {len(records)} events to {csv_path}.")

def check_overlaps(df_pending, df_created):
    """
    Compares pending events with created events.
    Returns a boolean series for df_pending.
    """
    if df_created.empty:
        return pd.Series([False] * len(df_pending))

    def is_match(row):
        # Summary match AND Start string match (start of string to avoid TZ issues if simple)
        # Note: df_pending['Begin'] is like "2026-01-01T07:00:00"
        # df_created['Begin'] is like "2026-01-01T07:00:00-05:00"
        mask = (df_created['Summary'] == row['Summary']) & \
               (df_created['Begin'].str.startswith(row['Begin']))
        return mask.any()

    return df_pending.apply(is_match, axis=1)
