# Implementation Plan - Event Time Ranges and Test Mode Refactor

Refactor the system to support time ranges (e.g., "7 am - 7:45 am EST") in Google Sheet column headers and enhance the CLI with a refined "Test Mode".

## Implementation Summary

### Time Parsing Logic
- Update `parse_time_est` in `src/sync_scheduler.py` to support headers like `7 am - 7:45 am EST`.
- If no range is found, default to a 10-minute duration.
- Returns a tuple: `(start_iso, end_iso, duration_mins)`.

### Data Handling
- Modify `fetch_google_sheets_data` in `src/google_sheets_data.py` to store end times and durations for each time slot.
- Update the `pending_events` data structure to include `End` and `Duration` fields.

### Event Creation & Test Mode
- Update `prepare_event_body` in `src/sync_scheduler.py` to include `{duration}` and `{end_time_iso}`.
- **Enhanced Test Mode**: When the `--limit` argument is provided:
    - Event summaries are prefixed with `TEST:`.
    - Attendees are removed to prevent notifications.

### Robustness
- Fix JSON escaping issues for multiline bio descriptions using `json.dumps` logic to ensure safe string replacement in the template.

---

## Verification Results

### Unit Tests
Verified the following cases in `tests/test_time_parsing.py`:
- `7 am EST` -> `07:00` to `07:10` (10 mins)
- `7 am - 7:45 am EST` -> `07:00` to `07:45` (45 mins)
- `11:30 pm - 12:15 am EST` -> `23:30` to `00:15` (45 mins) - *Handles midnight crossover*

### Dry-Run Verification
Verified via `python3 src/sync_scheduler.py --limit 5`:
- Single-time columns correctly show 10-minute durations.
- Time-range columns correctly show dynamic durations and updated summaries.
- "Test Mode" successfully prefixes summaries and clears guests.
