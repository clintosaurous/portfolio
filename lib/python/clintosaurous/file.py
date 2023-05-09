#!/opt/clintosaurous/venv/bin/python3 -Bu

""" Clintosaurous DDI Tools Commnon File Functions

Common directory and file related functions for the Clintosaurous DDI tools
environment.

This is intended as an internal module for the Clintosaurous DDI tools.

    import clintosaurous.file
"""


import atexit
import clintosaurous.datetime
import clintosaurous.log as log
import clintosaurous.opts
import os
import pathlib
import re
import sys
import yaml


VERSION = '1.0.0'
LAST_UPDATE = '2023-01-18'


_conf_path = False
etc = '/etc/clintosaurous'

# Default lock file timeout in seconds. Default: 12 hours in lock()
_lock_age = None
# Lock file path.
lock_file = f'/run/lock/{os.path.basename(sys.argv[0])}.pid'


# CLI options.
clintosaurous.opts.parser.add_argument(
    '-c', '--ddi-config',
    help="""
        Path to Clintosaurous Tools configuration file. Default:
        /etc/clintosaurous/ddi.yaml
    """,
    type=str,
    default='/etc/clintosaurous/ddi.yaml'
)


def conf(conf_path: str = None, fail_friendly: bool = True) -> dict:

    """ Retrieve DDI Configuration File Contents

    Reads in the Clintosaurous DDI tools configuration file.

        config = clintosaurous.file.conf()

    If `fail_friendly` is True, messages will be output to STDERR, but will
    be in a friendly format so a user can understand what the issue is, vs.
    a developer. Important for this function since it validates a user
    maintained file.

    Parameters:

    conf_path (str): Path to configuration file. Default: --config option.
    fail_friendly (bool): If there is an error, output user friendly message.

    Return:

    dict: Contents from the configuration file.

    Raises:

    TypeError: `conf_path` is not a `str`.

    KeyError: When required configuration keys do not exist.
    TypeError: When required configuration keys are not the correct type.
    """

    # Type hints.
    if conf_path is not None and not isinstance(conf_path, str):
        if fail_friendly:
            print(
                'The configuration path is expected to be the fully ' +
                'qualified file path. ' +
                'Example: /etc/clintosaurous/custom-ddi.yaml',
                file=sys.stderr
            )
            sys.exit(1)

        raise TypeError(
            f'`conf_path` expected `str`, received {type(conf_path)}')

    if not isinstance(fail_friendly, bool):
        raise TypeError(
            '`fail_friendly` expected `bool`, ' +
            f'received {type(fail_friendly)}'
        )

    # Set configuration path.
    if conf_path is not None:
        conf_file(conf_path)
    else:
        conf_path = conf_file()

    # If configuration file does not exist, return empty dictionary.
    if not os.path.exists(conf_path):
        return {}

    # If the file exists, read in file contents.
    with open(conf_path, newline='') as c:
        conf_data = yaml.safe_load(c)

    # Perform configuration validation.

    example = '\n'.join([
        ''
        'Example:',
        ''
        '  ---',
        '  username: clintosaurous',
        '  group: clintosuarous',
        '  mgmt-group: clintosaurous-mgmt',
        '  read-only-group: clintosaurous-ro',
        '  database:',
        '    host: mysql-server.example.com',
        '    username: clintosaurous',
        '    passwd: "secret"',
        '    ssl: false'
    ])

    ssl_example = \
        re.sub(r'ssl: false', 'ssl: true', example, re.I | re.M) + '\n'
    ssl_example += ('\n'.join([
        '    ssl_ca: /path/to/ssl/ca/certificate.pem',
        '    ssl_cert: /path/to/ssl/certicate.pem',
        '    ssl_key: /path/to/ssl/certicate.key'
    ]))

    # Ensure required root configuration values exist.
    for key in ['username', 'group', 'database']:
        if key not in conf_data:
            if fail_friendly:
                print(
                    f'The configuration option `{key}` is missing in ' +
                    f'the configuration.\n{example}',
                    file=sys.stderr
                )
                sys.exit(1)

            raise KeyError(f'`{key}` key missing')

    # Ensure root values are strings, except "database". It's a `dict`.
    for key in ['username', 'group']:
        if not isinstance(conf_data[key], str):
            if fail_friendly:
                print(
                    f'The configuration option `{key}` is expected to ' +
                    f'be a string value.\n{example}',
                    file=sys.stderr
                )
                sys.exit(1)

            raise TypeError(
                f'`{key}` expected `str`, received {type(conf_data[key])}')

    # Ensure "database" key is a `dict`.
    if not isinstance(conf_data["database"], dict):
        if fail_friendly:
            print(
                'The configuration option `database` is expected to ' +
                f'have sub-values in the configuration.\n{example}',
                file=sys.stderr
            )
            sys.exit(1)

        raise TypeError(
            '`database` expected `dict`, ' +
            f'received {type(conf_data["database"])}'
        )

    db_conf = conf_data["database"]

    for key in ['host', 'username', 'passwd', 'ssl']:
        if key not in db_conf:
            if fail_friendly:
                print(
                    f'The database configuration option `{key}` is ' +
                    f'missing in the configuration.\n{example}',
                    file=sys.stderr
                )
                sys.exit(1)

            raise KeyError(f'Database `{key}` missing')

    for key in ['host', 'username', 'passwd']:
        if not isinstance(db_conf[key], str):
            if fail_friendly:
                print(
                    f'The database configuration option `{key}` is ' +
                    f'expected to be a string value.\n{example}',
                    file=sys.stderr
                )
                sys.exit(1)

            raise TypeError(
                f'Database `{key}` expected `str`, ' +
                f'received {type(db_conf[key])}'
            )

    if not isinstance(db_conf["ssl"], bool):
        if fail_friendly:
            print(
                f'The database configuration option `ssl` is expected ' +
                f'to be a true/false value.\n{example}',
                file=sys.stderr
            )

        raise TypeError(
            'Database `ssl` expected `bool`, ' +
            f'received {type(db_conf["ssl"])}'
        )

    check_ssl = False
    if db_conf["ssl"]:
        check_keys = ['ssl_ca', 'ssl_cert', 'ssl_key']
        for key in check_keys:
            if key in db_conf:
                check_ssl = True
                break

    if check_ssl:
        for key in check_keys:
            if key not in db_conf:
                if fail_friendly:
                    print(
                        f'The database configuration option `{key}` is ' +
                        f'missing in the configuration.\n{ssl_example}',
                        file=sys.stderr
                    )
                    sys.exit(1)

                raise KeyError(
                    f'Database key `{key}` missing')

            if not isinstance(db_conf[key], str):
                raise TypeError(
                    f'Database `{key}` expected `bool`, ' +
                    f'received {type(db_conf[key])}'
                )

    return conf_data


def conf_file(conf_path: str = None) -> str:

    """ Retrieve and/or Set the DDI Configuration File Path

    Parameters:

    conf_path (str): Path to configuration file. Default: --config option.

    Return:

    str: Path to the configuration file.

    Raises:

    TypeError: `conf_path` is not a `str`.
    """

    # Type hints.
    if conf_path is not None and not isinstance(conf_path, str):
        raise TypeError(
            f'`conf_path` expected `str`, received {type(conf_path)}')

    # Use global variable _conf_path.
    global _conf_path

    # If user supplied path, return that.
    if conf_path:
        _conf_path = conf_path
        return _conf_path

    # If global path is already set, return it.
    if _conf_path:
        return _conf_path

    # Get the configuration file path from CLI options.
    opts = clintosaurous.opts.cli()
    _conf_path = opts.ddi_config

    return _conf_path


def datestamp(usr_time: int = None) -> str:

    """ Datestamp String Formatted For Use In File Name

    Returns a datestamp to be used for a file name.

    A Unix style timestamp can be supplied, otherwise current time is used.

        datestamp = clintosaurous.file.datestamp()

    Parameters:

    usr_time (int|float): User supplied Unix timestamp.

    Return:

    str: Date stamp in 'YYYY-MM-DD' format. Example: '2022-09-10'

    Raises:

    TypeError: `usr_time` is not an `int` or `float`.
    """

    # Type hints are handled by clintosaurous.datetime.datestamp().

    return clintosaurous.datetime.datestamp(usr_time)


def lock(age_out: int = 43200) -> str:

    """ Check Status of Current Run Time Lock File

    Checks if a current lock file exists and creates one if not.

        lock_file = clintosaurous.file.lock()

    If the lock file exists, it checks if the PID in the lock file is still
    running. If it is not a warning is thrown and a new lock file is created.

    If it is still running and the lock file is older than the age out timer,
    the script will throw a warning and attempt to kill the existing process.
    If the lock file age is within the age out timer, an error will be thrown
    and will exit with an error code.

    Lock file path will be placed at /run/lock/<script_name>.pid.

    Lock file will be removed on exit, or can be removed manually using
    clintosaurous.file.unlock().

    Note: If you have a long running process, it is recommended to run this
    occassionally to update the log file timestamp and avoid uninteneded
    process killing.

    Parameters:

    age_out (int): Time in seconds to age out a previously running process.
        This looks at the last modify time of the lock file and if it has not
        been updated within the age out time, the process will be killed.

    Return:

    str: Path to the lock file.

    Raises:

    TypeError: `age_out` is not an `int`.
    """

    # Type hints.
    if isinstance(age_out, bool) or not isinstance(age_out, int):
        raise TypeError(f'`age_out` expected `int`, received {type(age_out)}')

    # Use global lock file and lock file age out variables.
    global lock_file
    global _lock_age

    # Set default lock file age if not set already.
    if _lock_age is None:
        _lock_age = age_out
    else:
        age_out = _lock_age

    # Retrieve the run time process ID.
    pid = os.getpid()

    # If the file already exists.
    if os.path.exists(lock_file):
        # Read in process ID (PID) that created the fie.
        with open(lock_file) as f:
            file_pid = int(f.read().strip())

        # If the PID matches the current run time PID, update the last update
        # time on the lock file and return the lock file path.
        if file_pid == pid:
            pathlib.Path(lock_file).touch()
            return lock_file

        # Check if process is still running. Sending a kill signal of 0 will
        # not impact the existing process.
        try:
            os.kill(file_pid, 0)

        # If the process is not running, throw a warning and remove the
        # existing lock file.
        except OSError:
            log.wrn('Lock file exists, but process dead. Overriding lock.')
            os.remove(lock_file)

        # If the previous process is still running, check age out timer and
        # kill the process if it exceeds the age out timer.
        else:
            # If the last modify time on the lock file is older than the age
            # out, override the lock file.
            if os.path.getmtime(lock_file) > age_out:
                log.wrn('Lock file exists, but has passed age out timer.')
                log.wrn('Overriding lock.')

                # Kill existing process.
                os.kill(file_pid)
                try:
                    # Check if the previous process exited.
                    os.kill(file_pid, 0)
                except OSError:
                    # If the previous process failed to exit, throw an error
                    # and exit the current script with an error code.
                    log.err(f'Error killing process {file_pid}')
                    sys.exit(1)

            else:
                # If the previous process is within the age out timer, throw
                # an error and exit the current script with an error code.
                log.err(f'Existing process {file_pid} running!')
                sys.exit(1)

    # Create lock file for current process.
    with open(lock_file, "w") as file_obj:
        file_obj.write(str(pid))

    atexit.register(unlock)

    return lock_file


def timestamp(usr_time: int = None, tz: bool = True) -> str:

    """
    Generates a timestamp string for the Unix time supplied or for the
    current date usable in a file name.

        timestamp = clintosaurous.file.timestamp()

    Parameters:

    usr_time (int|float): User supplied Unix timestamp.
    tz (bool): Whether to append timezone to end of return.

    Return:

    str: Time stamp string in 'YYYY-MM-DD HH:MM:SS TZ' format. If tz is False,
    the time zone will be omitted. Example: '2022-09-10-08-25-10-edt'

    Raises:

    TypeError: `usr_time` is not an `int` or `float`.
    TypeError: `tz` is not a `bool`.
    """

    # Type hints are handled by clintosaurous.datetime.timestamp().

    return re.sub(
        r'\W+', '-',
        clintosaurous.datetime.timestamp(usr_time, tz=tz).lower()
    )


def unlock():

    """ Remove the Current Lock File On Script Exit

    This will be added to the exit processing using the `atexit` module. The
    `atexit` module will run this process on clean and Exception exits.
    """

    global lock_file

    # Delete existing lock file if exits.
    if os.path.exists(lock_file):
        os.remove(lock_file)
