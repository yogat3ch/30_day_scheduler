Can we create a function in @utils_calendar_general.py called `write_events_to_csv` which writes Google calendar event data returned by @fetch_calendar_events to a csv file?
The function will be similar to @export_existing_to_csv, and will take `events` and a `filename` as arguments. The function will write the events to a csv file with the following columns: 
 - Summary
 - Begin (Datetime)
 - Teacher (The text following the `:` in the `summary` field)
 - Date (The date of the event, extrapolated from the `start` datetime)
 - Day (The day of the week, extrapolated from the `start` datetime)
 - Start (The hour of the event start, extrapolated from the `start` datetime as a 24hr time in the format `HH:MM`)
 