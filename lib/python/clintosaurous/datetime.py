#!/opt/clintosaurous/venv/bin/python3 -Bu

""" Clintosaurous Tools Various Date and Time Functions

This is intended as an internal module for the Clintosaurous DDI tools.

Provides date and time operations for Clintosaurous tools scripts.

    import clintosaurous.datetime
"""

# Required modules.
import time
import clintosaurous.text


VERSION = '1.0.0'
LAST_UPDATE = '2023-01-04'


# Script start time for use with run_time()
start_time = time.time()


def datestamp(usr_time: int = None) -> str:

    """ Create a Timestamp Value

    Generates a datestamp string for the Unix time supplied

        file_datestamp = clintosaurous.file.datestamp()

    The current date is used if omitted. Format is "YYYY-MM-DD".

    Parameters:

    usr_time (int|float): User supplied Unix timestamp.

    Return:

    str: Date stamp.

    Raises:

    TypeError: `usr_time` is not an `int` or `float`.
    """

    # Type hints.
    if (
        usr_time is not None and (
            isinstance(usr_time, bool)
            or (not isinstance(usr_time, float)
                and not isinstance(usr_time, int))
        )
    ):
        raise TypeError(
            '`usr_time` expected `int` or `float`, ' +
            f'received {type(usr_time)}'
        )

    # Convert `float` values to `int`. This will drop any sub second data.
    if isinstance(usr_time, float):
        usr_time = int(usr_time)

    # Get time object for parsing the time from.
    if usr_time is not None:
        usr_time = time.localtime(usr_time)
    else:
        usr_time = time.localtime()

    return time.strftime("%Y-%m-%d", usr_time)


def run_time(delta_time: int = None, short: bool = False) -> str:

    """ Create a Run Time Breakdown String

    Returns a string with the run time of the number of seconds provided.

        delta_run_time = clintosaurous.file.run_time()

    If delta_time is omitted, time since script execution. There are two
    formats that can be returned. A long time description or a short one
    which can be specifed with the "short" option.

    Long format: 2 days, 2 hours, 2 minutes, 2 seconds
    Short format: DD:HH:MM:SS

    If there is not a value for one of the timeframes, they will not be
    returned. Exception is seconds is always returned, even if zero.

    Parameters:

    delta_time (int|float): Time difference to use for computation.
    short (bool): Whether to return data in short format. Default: False

    Return:

    str: Run time output.

    Raises:

    TypeError: `delta_time` is not an `int` or `float`.
    TypeError: `short` is not a `bool`.
    """

    # Type hints.
    if (
        delta_time is not None
        and not isinstance(delta_time, int)
        and not isinstance(delta_time, float)
    ):
        raise TypeError(
            '`delta_time` expected `int` or `float`, ' +
            f'received {type(delta_time)}'
        )
    if not isinstance(short, bool):
        raise TypeError(
            f'`short` expected `bool`, received {type(delta_time)}')

    # If `delta_time` was not supplied, set delta time to time since script
    # started.
    if delta_time is None:
        global start_time
        delta_time = time.time() - start_time

    # If delta time is zero, just return 0 seconds.
    if delta_time < 60:
        if short:
            delta_time = str(int(delta_time)).rjust(2, '0')
            return f'00:00:00:{delta_time}'
        return f'{round(delta_time, 2)} seconds'

    # Convert `float` values to `int`. This will drop any sub second data.
    elif isinstance(delta_time, float):
        delta_time = int(delta_time)

    # Get the break down of the delta time.
    days, hours, minutes, seconds = time_breakdown(delta_time)

    # The names of the values and the values being returned.
    return_labels = []
    return_values = []

    # List of values to check for data for.
    check_values = [
        ['day', days],
        ['hour', hours],
        ['minute', minutes],
        ['second', seconds],
    ]
    # Loop through the values to check for.
    for name, value in check_values:
        # If there is a value, append the current value and name.
        if value:
            return_labels.append(name)
            return_values.append(value)

        # If there is no value, but returning in short format, add value to
        # value list.
        elif short:
            return_values.append(0)

    # If returning in short format, build and return run time data.
    if short:
        return_values = [str(value).rjust(2, '0') for value in return_values]
        return ':'.join(return_values)

    return_data = []
    for i in range(len(return_labels)):
        name = clintosaurous.text.pluralize(
            return_labels[i], return_values[i])
        return_data.append(f'{return_values[i]} {name}')

    return ', '.join(return_data)


def time_breakdown(seconds: int) -> list:

    """ Break Seconds Down to Days, Hours, Minutes, and Seconds

    Breaks down the number of seconds into days, hours, minutes, and
    seconds.

    All are returned as integer objects.

    Parameters:

    seconds (int|float): Number of seconds to compute the breakdown.

    Return:

    list: List of broken down values. Format: [days, hours, minutes, seconds]

    Raises:

    TypeError: `seconds` is not an `int` or `float`.
    ValueError: `seconds` is not a positive number.
    """

    # Type hints.
    if (
        isinstance(seconds, bool)
        or (not isinstance(seconds, int) and not isinstance(seconds, float))
    ):
        raise TypeError(
            f'`seconds` expected `bool`, received {type(seconds)}')
    if (seconds < 0):
        raise ValueError(
            f'`seconds` must be a positive number, recieved {seconds}')

    # Convert a float to an integer.
    if isinstance(seconds, float):
        seconds = int(seconds)

    # If less than a minute, return passed value.
    if seconds < 60:
        return [0, 0, 0, seconds]

    values = []
    units = [86400, 3600, 60]   # In seconds: 1 day, 1 hour, 1 minute
    for unit_seconds in units:
        if seconds >= unit_seconds:
            values.append(int(seconds / unit_seconds))
            seconds = int(seconds % unit_seconds)
        else:
            values.append(0)

    values.append(seconds)

    return values


def timestamp(usr_time: int = None, tz: bool = True) -> str:

    """
    Generates a timestamp string for the Unix time supplied or for the
    current date.

    Format is "YYYY-MM-DD HH:MM:SS TZ". TZ is the local system's timezone.

    Parameters:

    usr_time (int|float): User supplied Unix timestamp.
    tz (bool): Whether to append timezone to end of return.

    Return:

    str: Time stamp string.

    Raises:

    TypeError: `usr_time` is not an `int` or `float`.
    TypeError: `tz` is not a `bool`.
    """

    # Type hints.
    if (
        usr_time is not None and (
            isinstance(usr_time, bool)
            or (not isinstance(usr_time, float)
                and not isinstance(usr_time, int))
        )
    ):
        raise TypeError(
            f'usr_time expected `float` or `int`, received {type(usr_time)}')
    if not isinstance(tz, bool):
        raise TypeError(f'tz expected `bool`, received {type(tz)}')

    if usr_time:
        usr_time = time.localtime(usr_time)
    else:
        usr_time = time.localtime()

    if tz:
        return time.strftime("%Y-%m-%d %H:%M:%S %Z", usr_time)
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S", usr_time)
