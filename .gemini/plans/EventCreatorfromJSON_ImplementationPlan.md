# Implementation Plan: EventCreatorfromJSON Notebook

Create a Jupyter notebook to automate the creation and management of Google Calendar events based on a JSONC schedule.

## Proposed Changes

### [NEW] [EventCreatorfromJSON.ipynb](file:///Users/stephenholsenbeck/Documents/Python/30-day_scheduler/EventCreatorfromJSON.ipynb)

#### Features
1.  **Configuration**: Define constants for file paths, calendar ID, and scopes.
2.  **Authentication**: Reuse OAuth logic to get `calendar_service`.
3.  **JSONC Parsing**: Use `JsoncParser` to load `ysc_cal.jsonc`.
4.  **Comparison Logic**:
    *   Fetch all events from the target calendar from `now` until the end of the year.
    *   Match events by `dateTime` and `summary` to avoid duplicates.
5.  **Export to CSV**: Add a cell to Save `existing_events` for manual auditing.
6.  **Creation**:
    *   Insert new events.
    *   Respect `TEST_MODE` (limit to 3 if True).
    *   Log created IDs to `logs/created_events.csv`.
7.  **Deletion**:
    *   Add a cell to delete events listed in the CSV.

## Verification Plan

### Automated Tests
- Run the notebook in `TEST_MODE = True`.
- Verify that only 3 events are identified for creation (if new).
- Verify the `logs/created_events.csv` is populated.

### Manual Verification
- Check the Google Calendar UI to confirm events are created with correct times and details.
- Test the deletion cell to ensure events can be cleaned up.
