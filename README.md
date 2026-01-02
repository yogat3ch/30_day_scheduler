# Google Calendar Spreadsheet Sync

A Python-based utility to synchronize teacher signup data from a Google Spreadsheet to a Google Calendar. This project streamlines the process of creating calendar events based on spreadsheet signups, with built-in overlap detection and customizable event templates.

## 🚀 Primary Workflow: Jupyter Notebook

The recommended way to use this project is through the **[sync_scheduler.ipynb](file:///Users/stephenholsenbeck/Documents/Python/30-day_scheduler/sync_scheduler.ipynb)** notebook. It provides an interactive, step-by-step interface for the entire synchronization process.

### Notebook Steps:

1.  **Setup and Authentication**: Initializes Google API services (Sheets and Calendar) and handles OAuth2 authentication.
2.  **Fetch Event Data**: Pulls signup and teacher contact information from your Google Sheet.
3.  **Overlap Detection**: Automatically syncs with the calendar to identify events that have already been created, preventing duplicates.
4.  **User Review and Pruning**: Displays a preview of pending events and allows you to interactively remove any overlaps before proceeding.
5.  **Event Creation**: Formats events using a template and creates them on the calendar, saving progress incrementally.
6.  **Cleanup (Optional)**: Provides a quick way to delete all events created in the current session if needed.

---

## 📋 Prerequisites

- Python 3.x
- Google Cloud Project with **Google Sheets API** and **Google Calendar API** enabled.
- `credentials.json` placed in the `.credentials/` directory.

## 🛠 Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    - `SPREADSHEET_ID`: Set in the first cell of the notebook.
    - `CALENDAR_ID`: Set in the first cell of the notebook.
    - `_calendar_event_template.jsonc`: Customize the event body using `{Variable}` notation.

## 📖 Alternative: CLI Usage (Advanced)

While the notebook is recommended, you can still run the synchronization via the command line:

**Test Run (No API calls):**
```bash
python3 src/sync_scheduler.py --test
```

**Live Run:**
```bash
python3 src/sync_scheduler.py --run
```

**Limited Run:**
```bash
python3 src/sync_scheduler.py --run --limit 5
```

## 📁 Directory Structure

- `sync_scheduler.ipynb`: Primary interactive workflow.
- `src/`: Core logic modules.
  - `sync_scheduler.py`: Event formatting and API interaction.
  - `google_sheets_data.py`: Data retrieval from Google Sheets.
  - `overlap_detection.py`: Logic for identifying existing events.
- `logs/`: Contains `created_events.csv` for tracking and historical record-keeping.
- `.credentials/`: Stores your `credentials.json` and OAuth tokens.

## ❓ Troubleshooting

- **Missing Columns**: Ensure your "Teacher Contact" sheet headers match the variables in your `_calendar_event_template.jsonc`.
- **Permissions**: If you encounter authentication errors, delete the `.json` token files in `.credentials/` and re-run the setup cell.
- **Jupyter Environment**: Ensure you have a Jupyter kernel installed (`pip install ipykernel`).
