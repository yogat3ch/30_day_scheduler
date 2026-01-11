Please create @EventCreatorfromJSON.ipynb notebook that will have the following variables and will create events in the calendar specified by CALENDAR_ID:
```python
CALENDAR_JSON = 'calendars/ysc/ysc_cal.jsonc'
CALENDAR_ID = 'cfa99d35ea82a15087d90134f9c69f98887c3afbcb8609251128809b25eedbe9@group.calendar.google.com'  # Replace with specific calendar ID if needed
CREATED_EVENTS_CSV = 'logs/created_events.csv'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 
          'https://www.googleapis.com/auth/calendar.events']

# Credentials Paths
TOKEN_PATH = '.credentials/token.json'
CREDS_PATH = '.credentials/credentials.json'
# Testing
TEST_MODE = True
```

The notebook should have the following functionality:
1. Read the calendar jsonc file, converting to JSON.
2. Read the calendar and pull a list of existing events from the current date until years end for comparison
3. Allow for printing the existing events to a CSV file.
4. Iterate through the calendar JSON and create events for each event that doesn't exist in the calendar.
5. Save the created events, including the event ID, to a CSV file in the logs directory, for ease of deletion.
6. Allow for deletion of events from the calendar based on the CSV file.

When `TEST_MODE` is set to True, the notebook should create only the first 3 events in the calendar.
