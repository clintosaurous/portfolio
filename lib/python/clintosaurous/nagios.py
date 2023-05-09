#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
This module contains common functions for Nagios monitoring scripts.

    from clintosuaour.nagios import *

    critical(message)
    ok(message)
    warning(message)
"""


import sys


VERSION = '1.0.0'
LAST_UPDATE = '2022-10-29'


def critical(msg: str) -> None:

    """
    This function prints out a critical issue message and exits with exit
    status 2.

        critical(msg)

    `msg`: Message to be printed before exiting. All messages are prepended
    with "CRITICAL - ".
    """

    # Type hints.
    if not isinstance(msg, str):
        print(
            f'CRITICAL: TypeError: msg expected `str`, received {type(msg)}')
        sys.exit(2)

    print(f'CRITICAL: {msg.strip()}')
    sys.exit(2)

# End: critical()


def ok(msg: str) -> None:

    """
    This function prints out an OK message and exits with exit status 0.

        warning(msg)

    `msg`: Message to be printed before exiting. All messages are prepended
    with "OK: ".
    """

    # Type hints.
    if not isinstance(msg, str):
        print(
            f'CRITICAL: TypeError: msg expected `str`, received {type(msg)}')
        sys.exit(2)

    print(f'OK: {msg.strip()}')
    sys.exit()

# End: ok()


def warning(msg: str) -> None:

    """
    This function prints out a warning issue message and exits with exit
    status 1.

        warning(msg)

    `msg`: Message to be printed before exiting. All messages are prepended
    with "WARNING: ".
    """

    # Type hints.
    if not isinstance(msg, str):
        print(
            f'CRITICAL: TypeError: msg expected `str`, received {type(msg)}')
        sys.exit(2)

    print(f'WARNING: {msg.strip()}')
    sys.exit(1)

# End: warning()
