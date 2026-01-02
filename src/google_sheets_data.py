import pandas as pd
import re
import datetime
from jsonc_parser.parser import JsoncParser
from sync_scheduler import parse_time_est

def fetch_google_sheets_data(sheets_service, spreadsheet_id, signup_sheet, contact_sheet, template_file):
    """
    Fetches contact and signup data from Google Sheets and prepares pending events.
    
    Args:
        sheets_service: Initialized Google Sheets API service.
        spreadsheet_id (str): ID of the spreadsheet.
        signup_sheet (str): Name of the signup sheet.
        contact_sheet (str): Name of the contact sheet.
        template_file (str): Path to the JSONC template file.
        
    Returns:
        tuple: (df_pending, teacher_map)
    """
    # 1. Fetch Contact Data
    contact_range = f"'{contact_sheet}'!A1:F100"
    contact_result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=contact_range).execute()
    contact_rows = contact_result.get('values', [])

    teacher_map = {}
    if contact_rows:
        contact_headers = contact_rows[0]
        contacts_df = pd.DataFrame(contact_rows[1:], columns=contact_headers)
        for _, row in contacts_df.iterrows():
            full_name = f"{row['First Name']} {row['Last Name']}".strip()
            teacher_map[full_name] = row.to_dict()
        print(f"Loaded {len(teacher_map)} teacher contacts.")

    # 2. Fetch Signup Data
    signup_range = f"'{signup_sheet}'!A1:Z50"
    signup_result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=signup_range).execute()
    signup_rows = signup_result.get('values', [])

    df_pending = pd.DataFrame()
    if signup_rows:
        header_row = signup_rows[2]
        time_slots = {}
        for i, header in enumerate(header_row):
            if i < 2: continue
            parsed_time = parse_time_est(header)
            if parsed_time:
                time_slots[i] = parsed_time
        
        pending_events = []
        
        for row_idx, row in enumerate(signup_rows):
            if row_idx < 3: continue
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
                if teacher_name not in teacher_map: continue
                
                contact_info = teacher_map[teacher_name]
                start_time_iso = time_slots[col_idx]
                
                start_dt = datetime.datetime.strptime(f"{date_str} {start_time_iso}", "%Y-%m-%d %H:%M")
                
                pending_events.append({
                    "Summary": f"10-Minute Guided Session: {teacher_name}",
                    "Begin": start_dt.isoformat(),
                    "Teacher": teacher_name,
                    "Contact": contact_info,
                    "Date": date_str,
                    "Day": day_of_week,
                    "Start": start_time_iso
                })

        df_pending = pd.DataFrame(pending_events)
        print(f"Found {len(df_pending)} events in Google Sheets.")
    
    return df_pending, teacher_map
