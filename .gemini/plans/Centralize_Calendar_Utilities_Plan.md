# Implementation Plan: Centralize Calendar Utilities

Refactor the codebase to consolidate shared Google Calendar and authentication logic into a single utility file.

## Proposed Changes

### [NEW] [utils_calendar_general.py](file:///Users/stephenholsenbeck/Documents/Python/30-day_scheduler/src/utils_calendar_general.py)
Move and consolidate the following functions:
- `get_google_services`: Unified authentication for Sheets and Calendar.
- `create_event`: Shared event insertion logic with backoff.
- `fetch_calendar_events`: Consolidated from `overlap_detection.py`.
- `delete_events_from_csv`: Consolidated from `EventCreatorfromJSON.ipynb`.
- `load_jsonc`: Helper for parsing JSONC files.

### [MODIFY] [sync_scheduler.py](file:///Users/stephenholsenbeck/Documents/Python/30-day_scheduler/src/sync_scheduler.py)
- Import shared functions from `utils_calendar_general`.
- Remove local definitions of `get_google_services` and `create_event`.

### [MODIFY] [overlap_detection.py](file:///Users/stephenholsenbeck/Documents/Python/30-day_scheduler/src/overlap_detection.py)
- Import `fetch_calendar_events` and `update_created_events_csv` (or use the one in utils).

### [MODIFY] [EventCreatorfromJSON.ipynb](file:///Users/stephenholsenbeck/Documents/Python/30-day_scheduler/EventCreatorfromJSON.ipynb)
- Replace internal functions with imports from `src.utils_calendar_general`.

### [MODIFY] [sync_scheduler.ipynb](file:///Users/stephenholsenbeck/Documents/Python/30-day_scheduler/sync_scheduler.ipynb)
- Update code cells to use the new utility imports.

## Verification Plan

### Automated Tests
- Run `EventCreatorfromJSON.ipynb` in `TEST_MODE` to verify sync and creation.
- Run `sync_scheduler.ipynb` Step 1 and Step 3 to verify overlap detection still works.

### Manual Verification
- Ensure API authentication still works (token refresh/generation).
- Verify that `logs/created_events.csv` is correctly updated.
