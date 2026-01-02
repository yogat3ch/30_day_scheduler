# Part 1: Overlap Detection Improvements

Here's the code for the @Overlap Detection section in the @sync_scheduler.ipynb file:

```python
if os.path.exists(CREATED_EVENTS_CSV):
    df_created = pd.read_csv(CREATED_EVENTS_CSV)
    print(f"Loaded {len(df_created)} already created events.")
    
    # Note: df_pending['Begin'] is naive, df_created['Begin'] might have TZ offset
    # Let's normalize for matching if they are the same format (ISO)
    
    # Mark overlaps
    df_pending['is_overlap'] = df_pending['Begin'].apply(
        lambda x: any(df_created['Begin'].str.startswith(x)) # Simple match by start string
    ) & df_pending['Summary'].isin(df_created['Summary'])
    
    overlaps = df_pending[df_pending['is_overlap'] == True]
    print(f"Detected {len(overlaps)} overlapping events.")
    display(overlaps)
else:
    df_pending['is_overlap'] = False
    df_created = pd.DataFrame(columns=['Summary', 'ID', 'Begin'])
    print("No created_events.csv found. Starting fresh.")
```

Can we rework this code to fetch the events from the Google Calendar to populate the:
  - start Datetime as `Begin`
  - the Event ID as `ID`
  - The Summary/Title as `Summary`
Then use this data to update the created_events.csv file when a variable `UPDATE_CREATED_EVENTS` is set to `True`? And put it in a script called overlap_detection.py?

# Part 2: Functionalize Google Sheets Data Fetching
Can we convert as much of this code as is reasonable from the chunk  `## Step 2: Fetch Event Data from Google Sheets` in @sync_scheduler.ipynb into a function called `fetch_google_sheets_data` and put it in a script called google_sheets_data.py, and provide instructions on how to refactor the chunk in the @sync_scheduler.ipynb file to consume global variables from @sync_scheduler.ipynb and import the function from google_sheets_data.py?

```python
# 1. Fetch Contact Data
contact_range = f"'{CONTACT_SHEET}'!A1:F100"
contact_result = sheets_service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range=contact_range).execute()
contact_rows = contact_result.get('values', [])

if contact_rows:
    contact_headers = contact_rows[0]
    contacts_df = pd.DataFrame(contact_rows[1:], columns=contact_headers)
    teacher_map = {}
    for _, row in contacts_df.iterrows():
        full_name = f"{row['First Name']} {row['Last Name']}".strip()
        teacher_map[full_name] = row.to_dict()
    print(f"Loaded {len(teacher_map)} teacher contacts.")

# 2. Fetch Signup Data
signup_range = f"'{SIGNUP_SHEET}'!A1:Z50"
signup_result = sheets_service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID, range=signup_range).execute()
signup_rows = signup_result.get('values', [])

if signup_rows:
    header_row = signup_rows[2]
    time_slots = {}
    for i, header in enumerate(header_row):
        if i < 2: continue
        parsed_time = parse_time_est(header)
        if parsed_time:
            time_slots[i] = parsed_time
    
    pending_events = []
    template_str = JsoncParser.parse_file(TEMPLATE_FILE)
    template_text = open(TEMPLATE_FILE, 'r').read()
    
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
            # Assume EST (-05:00) for comparison if not specified, but let's keep it simple for now
            
            pending_events.append({
                "Summary": f"10-Minute Guided Session: {teacher_name}",
                "Begin": start_dt.isoformat(), # This will be without TZ, adjust if needed
                "Teacher": teacher_name,
                "Contact": contact_info,
                "Date": date_str,
                "Day": day_of_week,
                "Start": start_time_iso
            })

    df_pending = pd.DataFrame(pending_events)
    print(f"Found {len(df_pending)} events in Google Sheets.")
    display(df_pending.head())
```
# Part 3 Separation of Concerns: 
Can we convert all the remaining function declarations in the @sync_scheduler.ipynb file to Python functions in the @sync_scheduler.py file and import them into the sync_scheduler.ipynb file? I'll then remove them from the ipynb file.



