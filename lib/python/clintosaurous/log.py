#!/opt/clintosaurous/venv/bin/python3 -Bu

""" Clintosaurous DDI Tools Logging Module

This module provides logging functionality for Clintosaurous tools.

Facilitates logging functions.

    +-------------------+
    |     Log Levels    |
    +---------+---------+
    | 0 = EMR | 4 = WRN |
    | 1 = ALR | 5 = LOG |
    | 2 = CRI | 6 = INF |
    | 3 = ERR | 7 = DBG |
    +---------+---------+

Log level (5) is the default log level.
"""


import clintosaurous.opts
import clintosaurous.datetime
import os
import sys
import syslog as slog


VERSION = '1.0.0'
LAST_UPDATE = '2023-01-18'


# CLI options.
_parser_log_group = clintosaurous.opts.parser.add_argument_group('logging')

_parser_log_group.add_argument(
    '--log-append',
    action='store_true',
    help="""
        Append existing log file if it exists. Default is to create a new
        file.
    """
)
_parser_log_group.add_argument(
    '--log-file',
    type=str,
    help='Output log file name. If omitted, STDOUT and STDERR used.'
)
_parser_log_group.add_argument(
    '--no-log-stderr',
    action='store_true',
    help='Disables sending error messages to STDERR. Output to STDOUT only.'
)
_parser_log_group.add_argument(
    '-q', '--quiet',
    action='store_true',
    help="""
        Set logging to quiet. Only output error messages or more severe
        (level 4 or lower). Overrides --log-level, --log-info, and --debug.
    """
)
_parser_log_group.add_argument(
    '-s', '--silent',
    action='store_true',
    help='Suppresses all logging output.'
)
_parser_log_group.add_argument(
    '-S', '--syslog',
    action='store_true',
    help='Output log messages to syslog, not STDOUT/STDERR.'
)
_parser_log_group.add_argument(
    '-v', '--verbose',
    action='count',
    help='Enable verbose logging. Multiple increases verbose level.'
)


# Predefined variables.
log_levels = ['EMR', 'ALR', 'CRI', 'ERR', 'WRN', 'LOG', 'INF', 'DBG']
_out_level = None
_syslog_proc = os.path.basename(sys.argv[0])
_syslog_levels = [
    slog.LOG_EMERG, slog.LOG_ALERT, slog.LOG_CRIT, slog.LOG_ERR,
    slog.LOG_WARNING, slog.LOG_NOTICE, slog.LOG_INFO, slog.LOG_DEBUG
]


def emr(msg: str, syslog: bool = False) -> None:

    """ Output Emergency Level Log Messages

    Output emergency level (0) timestamped log messages to STDERR.

    `msg` can be a single string or a list of strings to output. All strings
    will be split on linefeeds and have a separate log message for each.

    CLI option `--quiet` does not suppress these messages.

    Parameters:

    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints are handled by _msg_out().

    if msg:
        _msg_out(0, msg, syslog=syslog)


def alr(msg: str, syslog: bool = False) -> None:

    """ Output Alarm Level Log Messages

    Output alarm level (1) timestamped log messages to STDERR.

    `msg` can be a single string or a list of strings to output. All strings
    will be split on linefeeds and have a separate log message for each.

    CLI option `--quiet` does not suppress these messages.

    Parameters:

    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints are handled by _msg_out().

    if msg:
        _msg_out(1, msg, syslog=syslog)


def cri(msg: str, syslog: bool = False) -> None:

    """ Output Critical Level Log Messages

    Output critical level (2) timestamped log messages to STDERR.

    `msg` can be a single string or a list of strings to output. All strings
    will be split on linefeeds and have a separate log message for each.

    CLI option `--quiet` does not suppress these messages.

    Parameters:

    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints are handled by _msg_out().

    if msg:
        _msg_out(2, msg, syslog=syslog)


def err(msg: str, syslog: bool = False) -> None:

    """ Output Error Level Log Messages

    Output error level (3) timestamped log messages to STDERR.

    `msg` can be a single string or a list of strings to output. All strings
    will be split on linefeeds and have a separate log message for each.

    CLI option `--quiet` does not suppress these messages.

    Parameters:

    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints are handled by _msg_out().

    if msg:
        _msg_out(3, msg, syslog=syslog)


def wrn(msg: str, syslog: bool = False) -> None:

    """ Output Warning Level Log Messages

    Output warning level (4) timestamped log messages to STDERR.

    `msg` can be a single string or a list of strings to output. All strings
    will be split on linefeeds and have a separate log message for each.

    CLI option `--quiet` does not suppress these messages.

    Parameters:

    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints are handled by _msg_out().

    if msg:
        _msg_out(4, msg, syslog=syslog)


def log(msg: str, syslog: bool = False) -> None:

    """ Output Log Level Log Messages

    Output log level (5) timestamped log messages to STDOUT.

    `msg` can be a single string or a list of strings to output. All strings
    will be split on linefeeds and have a separate log message for each.

    CLI option `--quiet` suppresses these messages.

    Parameters:

    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints are handled by _msg_out().

    if msg:
        _msg_out(5, msg, syslog=syslog)


def inf(msg: str, syslog: bool = False) -> None:

    """ Output Informational Level Log Messages

    Output informational level (6) timestamped log messages to STDOUT.

    `msg` can be a single string or a list of strings to output. All strings
    will be split on linefeeds and have a separate log message for each.

    Output is suppressed unless `--info` or `--debug` options are set.

    Parameters:

    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints are handled by _msg_out().

    if msg:
        _msg_out(6, msg, syslog=syslog)


def dbg(msg: str, syslog: bool = False) -> None:

    """ Output Debug Level Log Messages

    Output debug level (7) timestamped log messages to STDOUT.

    `msg` can be a single string or a list of strings to output. All strings
    will be split on linefeeds and have a separate log message for each.

    Output is suppressed unless `--debug` option is set.

    Parameters:

    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints are handled by _msg_out().

    if msg:
        _msg_out(7, msg, syslog=syslog)


def log_level(level: int = None) -> int:

    """ Retrieve Or Update the Current Logging Level

    Retrieve the current logging level or set a new logging level. This is a
    global update.

    Set to -1 to disable logging.

    Parameters:

    level (int): New logging level. Set to -1 to disable logging. Default: 5

    Return:

    int: Current logging level.

    Raises:

    TypeError: `level` is not an `int`.
    """

    # Type hints.
    if (level is not None and (
        isinstance(level, bool) or not isinstance(level, int)
    )):
        raise TypeError(f'`level` expected `int`, received {type(level)}')

    global _out_level

    opts = clintosaurous.opts.cli()

    if level is not None:
        _out_level = level
    elif _out_level is None:
        if opts.silent:
            _out_level = -1
        elif opts.quiet:
            _out_level = 4
        elif opts.verbose and opts.verbose == 1:
            _out_level = 6
        elif opts.verbose:
            _out_level = 7
        else:
            _out_level = 5

    return _out_level


def _msg_out(level: int, msg: str, syslog: bool = False) -> None:

    """ Outputs Log Message to Appropriate Facility

    Output the log message(s) to the appropriate facility: file, STDERR,
    STDOUT, or syslog.

    Internal only function and should not be called directly.

    Parameters:

    level (int): Log level for message(s) being output.
    msg (str|list): Single string or list of messages to output.
    syslog (bool): Output messages as syslog entries instead of STDOUT/STDERR.
        Default: False

    Raises:

    TypeError: `level` is not an `int.
    TypeError: `msg` is not a `str` or `list`.
    TypeError: `syslog` is not a `bool`.
    """

    # Type hints.
    if not isinstance(level, int):
        raise TypeError(f'`level` expected `int`, received {type(level)}')
    if not isinstance(msg, str) and not isinstance(msg, list):
        raise TypeError(
            f'`msg` expected `str` or `list`, received {type(msg)}')
    if not isinstance(syslog, bool):
        raise TypeError(f'`syslog` expected `str`, received {type(syslog)}')

    global log_levels, _syslog_levels, _syslog_proc

    # If a string was supplied, convert it to a list.
    if not isinstance(msg, list):
        msg = [msg]

    # Validate the logging level includes this message's level.
    if level > log_level():
        return

    opts = clintosaurous.opts.cli()

    # Log level display name to prepend the messages with.
    display_level = log_levels[level]

    # Timestamp to prepend to the log messages.
    timestamp = clintosaurous.datetime.timestamp()

    # Set the output destination file handler.
    if opts.log_file:
        out = open(opts.log_file, "a")

    # Output is written directly to STDOUT and STDERR vs. using print.
    # If you have multiple processes outputting to your log, they can collide
    # and have their text intermingled. Writing to them directly locks them
    # until our writes have completed. The other processes trying to write
    # will wait in line.
    elif opts.no_log_stderr or level >= 5:
        out = sys.stdout
    else:
        out = sys.stderr

    # Loop through each user supplied message.
    for msg in msg:
        # Split multiline messages into individual log messages.
        for line in msg.split("\n"):
            # If outputting to syslog.
            if syslog or opts.syslog:
                slog.openlog(_syslog_proc, facility=slog.LOG_LOCAL2)
                slog.syslog(_syslog_levels[level], line.strip())
                slog.closelog()

            else:
                out.write(f'{timestamp}: {display_level}: {line.rstrip()}\n')

    # If outputting to a file, close the file.
    if opts.log_file:
        out.close()
