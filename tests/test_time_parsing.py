import datetime
import re
from src.sync_scheduler import parse_time_est

def test_parse_time_est():
    test_cases = [
        ("7 am EST", ("07:00", "07:10", 10)),
        ("7:30 pm EST", ("19:30", "19:40", 10)),
        ("7 am - 7:45 am EST", ("07:00", "07:45", 45)),
        ("11:30 pm - 12:15 am EST", ("23:30", "00:15", 45)),
        ("7 am PST | 8 am EST", ("08:00", "08:10", 10)),
        ("7 am - 7:45 am EST | 6 am CST", ("07:00", "07:45", 45)),
    ]

    for header, expected in test_cases:
        result = parse_time_est(header)
        assert result == expected, f"Failed for '{header}': expected {expected}, got {result}"
        print(f"PASSED: '{header}' -> {result}")

if __name__ == "__main__":
    try:
        test_parse_time_est()
        print("\nAll time parsing tests passed!")
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
