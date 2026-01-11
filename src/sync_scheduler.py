import os
import re
import json
import datetime
import pandas as pd
import backoff
from googleapiclient.errors import HttpError
from jsonc_parser.parser import JsoncParser
from utils_calendar_general import get_google_services, create_calendar_event

# --- Configuration ---
SPREADSHEET_ID = '10Z993MrZHH0Da_pXEFZoo0MBdxKhf619fZSuuvaAdlQ'
SIGNUP_SHEET = 'Signup'
CONTACT_SHEET = 'Teacher Contact'
CALENDAR_ID = 'b45a2d5121fed950d815cfa167dd4b3a6aa74c5d62fea928702e6f4300d96545@group.calendar.google.com'  # Replace with specific calendar ID if needed
TEMPLATE_FILE = '_calendar_event_template.jsonc'
CREATED_EVENTS_CSV = 'logs/created_events.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 
          'https://www.googleapis.com/auth/calendar.events']

# Credentials Paths
TOKEN_PATH = '.credentials/token.json'
CREDS_PATH = '.credentials/credentials.json'

# --- Helper Functions ---

def get_services():
    return get_google_services(TOKEN_PATH, CREDS_PATH, SCOPES)

def parse_time_est(header_str):
    """
    Extracts time from headers like '7 am CST | 1 pm GMT | 8 am EST'
    Specifically looks for the 'am/pm EST' part as requested.
    """
    match = re.search(r'(\d+(?::\d+)?\s*[ap]m)\s*EST', header_str, re.IGNORECASE)
    if not match:
        # Fallback to first available time if EST isn't found
        match = re.search(r'(\d+(?::\d+)?\s*[ap]m)', header_str, re.IGNORECASE)
    
    if match:
        time_str = match.group(1).lower().replace(' ', '')
        # Convert to 24h format for ISO
        if 'pm' in time_str and '12' not in time_str:
            h = int(time_str.replace('pm', '').split(':')[0]) + 12
            m = time_str.replace('pm', '').split(':')[1] if ':' in time_str else '00'
            return f"{h:02d}:{m}"
        elif 'am' in time_str and '12' in time_str:
            m = time_str.replace('am', '').split(':')[1] if ':' in time_str else '00'
            return f"00:{m}"
        else:
            time_part = time_str.replace('am', '').replace('pm', '')
            h = int(time_part.split(':')[0])
            m = time_part.split(':')[1] if ':' in time_part else '00'
            return f"{h:02d}:{m}"
    return None

def col_to_letter(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def validate_template(template_path):
    try:
        JsoncParser.parse_file(template_path)
        with open(template_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"\nCRITICAL ERROR: {TEMPLATE_FILE} is not valid JSONC.")
        print(f"Details: {str(e)}")
        raise SystemExit(1)

def prepare_event_body(row, template_text):
    """
    Prepares the event JSON body by substituting variables into the template.
    """
    # row is expected to have 'Date', 'Start', 'Day', and 'Contact'
    start_dt = datetime.datetime.strptime(f"{row['Date']} {row['Start']}", "%Y-%m-%d %H:%M")
    end_dt = start_dt + datetime.timedelta(minutes=10)
    end_time_iso = end_dt.strftime("%H:%M")
    
    vars = {
        "date": row['Date'],
        "day_of_week": row['Day'],
        "time_iso": row['Start'],
        "end_time_iso": end_time_iso,
    }
    vars.update(row['Contact'])
    
    event_json_str = template_text
    for key, val in vars.items():
        escaped_val = json.dumps(str(val))[1:-1]
        event_json_str = event_json_str.replace(f"{{{key}}}", escaped_val)
    
    return JsoncParser.parse_str(event_json_str)

def create_event(service, calendar_id, event_body):
    """
    Inserts an event into the Google Calendar using the shared utility.
    """
    return create_calendar_event(service, calendar_id, event_body)

def main(dry_run=True, test_teacher=None, limit=None):
    if dry_run:
        print("\n[DRY RUN MODE] Use --run to actually create events.")
    
    sheets_service, calendar_service = get_services()

    # 0. Validate Template early
    template_str = validate_template(TEMPLATE_FILE)
    
    # 1. Fetch Contact Data
    contact_range = f"'{CONTACT_SHEET}'!A1:F100"
    contact_result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=contact_range).execute()
    contact_rows = contact_result.get('values', [])
    
    if not contact_rows:
        print("No contact data found.")
        return

    contact_headers = contact_rows[0]
    contacts_df = pd.DataFrame(contact_rows[1:], columns=contact_headers)
    
    # Mapping unique names to their full contact dict
    teacher_map = {}
    for _, row in contacts_df.iterrows():
        full_name = f"{row['First Name']} {row['Last Name']}".strip()
        teacher_map[full_name] = row.to_dict()

    # 2. Fetch Signup Data
    signup_range = f"'{SIGNUP_SHEET}'!A1:Z50" # Adjust range as needed
    signup_result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=signup_range).execute()
    signup_rows = signup_result.get('values', [])

    if not signup_rows:
        print("No signup data found.")
        return

    # Header is at index 2 (Row 3)
    header_row = signup_rows[2]
    time_slots = {} # col_index -> time_iso
    for i, header in enumerate(header_row):
        if i < 2: continue # Skip first two columns (Instructions/Dates)
        parsed_time = parse_time_est(header)
        if parsed_time:
            time_slots[i] = parsed_time

    # 3. Iterate and Process
    errors = []
    events_to_create = []
    preview_data = []

    for row_idx, row in enumerate(signup_rows):
        if row_idx < 3: continue # Skip instructions and headers
        
        # Column B (idx 1) is Date: "Weekday, YYYY-MM-DD"
        if len(row) < 2: continue
        date_raw = row[1]
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', date_raw)
        if not date_match: continue
        date_str = date_match.group(0)
        
        day_of_week = date_raw.split(',')[0].strip()

        for col_idx, teacher_name in enumerate(row):
            if col_idx not in time_slots: continue
            if not teacher_name or teacher_name.strip() == "": continue
            
            teacher_name = teacher_name.strip()
            
            # Filter if test_teacher is provided
            if test_teacher and teacher_name != test_teacher:
                continue

            if teacher_name not in teacher_map:
                r1c1 = f"R{row_idx+1}C{col_idx+1}"
                errors.append(f"Error: No email found for '{teacher_name}' at {r1c1}")
                continue
            
            contact_info = teacher_map[teacher_name]
            start_time_iso = time_slots[col_idx]
            
            # Calculate end time (10 mins later)
            start_dt = datetime.datetime.strptime(f"{date_str} {start_time_iso}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + datetime.timedelta(minutes=10)
            end_time_iso = end_dt.strftime("%H:%M")

            # Prepare substitution variables
            vars = {
                "date": date_str,
                "day_of_week": day_of_week,
                "time_iso": start_time_iso,
                "end_time_iso": end_time_iso,
            }
            vars.update(contact_info) # Adds {First Name}, {Last Name}, etc.

            # Substitute in template safely
            event_json_str = template_str
            for key, val in vars.items():
                # We dump the value to JSON to ensure high/low characters and quotes are escaped
                # Then we strip the surrounding quotes that json.dumps adds to strings
                escaped_val = json.dumps(str(val))[1:-1]
                event_json_str = event_json_str.replace(f"{{{key}}}", escaped_val)
            
            try:
                event_data = JsoncParser.parse_str(event_json_str)
                events_to_create.append(event_data)

                # Collect preview info
                preview_data.append({
                    "Event Name": event_data.get('summary'),
                    "Event Start Time": event_data['start'].get('dateTime'),
                    "Event End Time": event_data['end'].get('dateTime'),
                    "Event Guest Name(s)": ", ".join([a.get('email', '') for a in event_data.get('attendees', [])])
                })
            except Exception as e:
                r1c1 = f"R{row_idx+1}C{col_idx+1}"
                print(f"\nERROR: Failed to parse generated JSON for {teacher_name} at {r1c1}")
                print(f"Parsing error: {str(e)}")
                # Potentially print the failing JSON for debugging
                # print(f"Offending JSON:\n{event_json_str}")
                continue

    # 4. Report Errors
    if errors:
        print("\n--- Matching Errors ---")
        for err in errors:
            print(err)

    # 5. Confirmation and Limiting
    if not events_to_create:
        print("\nNo events found to create.")
        return

    # Display Preview Table
    df_preview = pd.DataFrame(preview_data)
    print("\n--- Event Preview ---")
    print(df_preview.to_string(index=False))
    print(f"\nTotal events found: {len(events_to_create)}")

    if limit:
        print(f"Limit applied: only the first {limit} event(s) will be processed.")
        events_to_create = events_to_create[:limit]

    # Ask for confirmation if running live
    if not dry_run:
        confirm = input(f"\nProceed with creating {len(events_to_create)} events? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled by user.")
            return

        # 6. Create Events
        created_records = []
        for ev in events_to_create:
            try:
                created_event = calendar_service.events().insert(calendarId=CALENDAR_ID, body=ev).execute()
                print(f"Created event: {created_event.get('htmlLink')}")
                created_records.append({
                    'Summary': created_event.get('summary'),
                    'ID': created_event.get('id')
                })
            except HttpError as error:
                print(f"An error occurred: {error}")
        
        if created_records:
            df_created = pd.DataFrame(created_records)
            if os.path.exists(CREATED_EVENTS_CSV):
                df_created.to_csv(CREATED_EVENTS_CSV, mode='a', header=False, index=False)
            else:
                df_created.to_csv(CREATED_EVENTS_CSV, index=False)
            print(f"\nSuccessfully updated {CREATED_EVENTS_CSV} with {len(created_records)} new event records.")
    else:
        print("\n[DRY RUN] No events were created.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sync Spreadsheet to Google Calendar.')
    parser.add_argument('--run', action='store_true', help='Actually create events in the calendar.')
    parser.add_argument('--test', action='store_true', help='Only process events for Stephen Holsenbeck.')
    parser.add_argument('--limit', type=int, help='Limit the number of events to create.')
    
    args = parser.parse_args()
    
    main(dry_run=not args.run, test_teacher="Stephen Holsenbeck" if args.test else None, limit=args.limit)
