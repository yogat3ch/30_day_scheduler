# Google Calendar Spreadsheet Sync

A Python-based utility to synchronize teacher signup data from a Google Spreadsheet to a Google Calendar. It features a customizable JSONC template for event details, a comprehensive preview system, and automated event tracking for easy cleanup.

## Key Features
- **CSV Export**: Automatically records created event names and IDs to `created_events.csv`.
- **User Confirmation**: Displays a preview table of all events and asks for approval before calling the API.
- **Event Limiting**: Use the `--limit <N>` flag to run a live test with a small sample of events.
- **Easy Cleanup**: Use `event_delete.py` to remove events tracked in the CSV.
- **Efficient Mapping**: Pre-fetches teacher contact info to minimize API calls and maps variables directly from "Teacher Contact" column headers.
- **Detailed Errors**: Reports unmatched teachers with their exact grid location (e.g., `R5C3`).
- **Timezone Awareness**: Start times are parsed from column headers, focusing on EST.

## Prerequisites
- Python 3.x
- Google Cloud Project with Sheets and Calendar APIs enabled.
- `credentials.json` placed in the project root.

## Setup
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Initial Authentication & Test
Since this is the first run, the script needs you to authorize access to your Google account.
Run the script for a single teacher to authorize and see a preview:
```bash
python3 sync_scheduler.py --test
```
A browser window will open for OAuth2 authorization. Once authorized, the script will perform a **Dry Run**.

### 2. Create Real Events
Run the script with the `--run` flag to create events. You will be prompted to confirm the events shown in the preview table:
```bash
python3 sync_scheduler.py --run
```

### 3. Verify with a Limited Run
To create just a few events to verify they appear correctly in your calendar:
```bash
python3 sync_scheduler.py --run --limit 2
```

### 4. Cleanup / Delete Events
To remove the events created in a previous run:
```bash
python3 event_delete.py
```
This reads `created_events.csv`, deletes the events from your calendar, and removes the CSV file.

## Configuration
- `SPREADSHEET_ID`: Update in `sync_scheduler.py` if using a different sheet.
- `CALENDAR_ID`: Set to `primary` or a specific Calendar ID.
- `_calendar_event_template.jsonc`: Customize the event body, summary, and location using `{Variable}` notation.

## Troubleshooting
- **Missing Columns**: Ensure your "Teacher Contact" sheet has headers that match the variables in the template (e.g., `First Name`, `Last Name`, `Bio`).
- **Permissions**: If you get a "Scope" error, delete `token.json` and run the script again.
