from datetime import datetime, timedelta


def nanoseconds_to_datetime(nanoseconds,filename = False):
    # Convert nanoseconds to seconds
    seconds = nanoseconds // 1_000_000_000
    # Create datetime object from seconds
    dt = datetime.utcfromtimestamp(seconds)
    # Return formatted datetime string
    if filename:
        return dt.strftime('%Y%m%d_%H%M%S')
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def datetime_to_nanoseconds(dt_str):
    # Parse the datetime string to datetime object
    dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    # Convert datetime to seconds since epoch
    seconds = int(dt.timestamp())
    # Convert seconds to nanoseconds
    nanoseconds = seconds * 1_000_000_000
    return nanoseconds


# Example usage
# print(nanoseconds_to_datetime(1625150096000000000))
# print(datetime_to_nanoseconds('2021-07-01 12:34:56'))


def add_to_timestamp(timestamp, hours=0, minutes=0, seconds=0):
    """
    Add hours, minutes, and seconds to a Unix timestamp.

    Parameters:
    timestamp (int): The original Unix timestamp.
    hours (int): Number of hours to add. Defaults to 0.
    minutes (int): Number of minutes to add. Defaults to 0.
    seconds (int): Number of seconds to add. Defaults to 0.

    Returns:
    int: The new Unix timestamp after adding the specified time.
    """

    # Convert the original timestamp to a datetime object
    original_datetime = datetime.fromtimestamp(timestamp/1000)

    # Create a timedelta with the specified time to add
    time_to_add = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    # Add the time to the original datetime
    new_datetime = original_datetime + time_to_add

    # Convert back to Unix timestamp to milliseconds and return
    return int(new_datetime.timestamp() * 1000)

def convert_milliseconds_to_nanoseconds(milliseconds):
    """
    Convert milliseconds to nanoseconds.

    Parameters:
    milliseconds (int): The number of milliseconds.

    Returns:
    int: The number of nanoseconds.
    """
    return milliseconds * 1_000_000


