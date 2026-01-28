# Implement `write_events_to_csv` Function

The goal is to add a new utility function `write_events_to_csv` to `src/utils_calendar_general.py` that exports Google Calendar events to a CSV file with specific formatted columns.

## Proposed Changes

### utils_calendar_general.py

#### [MODIFY] [utils_calendar_general.py](file:///Users/stephenholsenbeck/Documents/Python/30-day_scheduler/src/utils_calendar_general.py)

Add the `write_events_to_csv(events, filename)` function.

The function will:
1. Ensure the destination directory exists.
2. Iterate through the `events` list.
3. Extract and transform the following fields:
    - `Summary`: The event title (`summary`).
    - `Begin (Datetime)`: The `start.dateTime` (or `start.date` for all-day events).
    - `Teacher`: Extracted from the `summary` by splitting at the first `:`. If no `:` exists, it will be empty or the whole summary depending on preferred behavior (I'll assume empty if not found).
    - `Date`: Extracted as `YYYY-MM-DD` from the start datetime.
    - `Day`: The day of the week (e.g., Monday, Tuesday).
    - `Start`: The start time in `HH:MM` 24-hour format.
4. Create a pandas DataFrame and save it to the specified `filename`.

## Verification Plan

### Automated Tests
I will create a temporary test script `test_csv_export.py` that:
1. Mocks a few calendar events.
2. Calls `write_events_to_csv`.
3. Checks if the file is created and contains the expected columns and values.

### Manual Verification
1. I will ask the user to run a cell in their notebook calling the new function with real data to confirm it meets their expectations.
