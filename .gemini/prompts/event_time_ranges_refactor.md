# Refactor Google Sheet Data Fetching and Event Creation to account for time range specifications in column headings
We need to refactor the `fetch_google_sheets_data` function in @google_sheets_data.py and the `prepare_event_body` function in @sync_scheduler.pyto account for time range specifications in the column headings. 

## Column Heading Format Update
The current column headings look like this:

```
7 am EST | 6 am CST | 12 pm GMT  | 1 pm CET | 5:30pm IST |  8 pm China ST | 1 am Australia 
```

Some column headers will now have time ranges in the first time slot, like this:

```
7 am - 7:45 am EST | 6 am CST | 12 pm GMT  | 1 pm CET | 5:30pm IST |  8 pm China ST | 1 am Australia 
```
These time ranges may use time signatures like 7, or 7:00 which should be parsed as 7:00 am. The am or pm designator may vary in case, and may or may not be separated by a space. All times will have the three letter time zone designator before the pipe character separating one time zone from another.


### Consequential DF Modifications
The data frame should be modified to have a `start` and `end` column for each time slot.

### Column Heading Handling
If a column heading has a time range, we should parse the start and end times to the `start` and `end` columns. If no time range is specified, the time should be parsed as the start of the time slot and the slot should be assumed to be 10 minutes long. 

### Event Body Handling
The `prepare_event_body` function should be modified to use the `start` and `end` columns from the data frame to create the event body. The `summary` field should be updated to include the `duration` of the event, where it's now specified in @_calendar_event_template.jsonc.