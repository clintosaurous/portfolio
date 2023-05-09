#!/opt/clintosaurous/venv/bin/python3 -Bu

""" pymysql Wrapper Module to Simplify Database Connectivity

This is intended as an internal module for the Clintosaurous DDI tools.

    import clintosaurous.db
"""


import atexit
import clintosaurous.file
import clintosaurous.log as log
import clintosaurous.opts
import os
import pymysql
import re


VERSION = '1.0.0'
LAST_UPDATE = '2023-01-18'


_connections = []


# CLI options.
_parser_db_group = \
    clintosaurous.opts.parser.add_argument_group("database options")
_parser_db_group.description = """
    Data base connectivity options. These are not required on the command
    line and can be supplied during database connection setup.
"""

_parser_db_group.add_argument(
    '--db-host',
    help="""
        Database server DNS name or IP address. No default, but a default
        can be supplied in the Clintosaurous global configuration file.
    """,
    type=str
)
_parser_db_group.add_argument(
    '--db-username',
    help="""
        Database username. No default, but a default should be supplied in the
        Clintosaurous global configuration file.
    """,
    type=str
)
_parser_db_group.add_argument(
    '--db-passwd',
    help="""
        Database user password. No default, but a default can be supplied in
        the Clintosaurous global configuration file.
    """,
    type=str
)
_parser_db_group.add_argument(
    '--db-name',
    help='Database name. Default: None.',
    type=str
)

_parser_db_group.add_argument(
    '--db-ssl',
    help="""
        Enable MySQL SSL connectivity. Default: False, but can be supplied in
        the Clintosaurous global configuration file.
    """,
    action="store_true"
)
_parser_db_group.add_argument(
    '--db-ssl-ca',
    help="""
        Path to SSL certificate authority (CA) file for the SSL certificate.
        Default: None, but can be set in the Clintosaurous global
        configuration file.
    """,
    type=str
)
_parser_db_group.add_argument(
    '--db-ssl-cert',
    help="""
        Path to SSL certificate file for the SSL certificate.
        Default: None, but can also be set in the Clintosaurous global
        configuration file.
    """,
    type=str
)
_parser_db_group.add_argument(
    '--db-ssl-key',
    help="""
        Path to SSL certificate private key file for the SSL certificate.
        Default: None, but can also be set in the Clintosaurous global
        configuration file.
    """,
    type=str
)


def _atexit() -> None:

    """ Code To Execute on Script Exit

    Close all database connections.
    """

    for db in _connections:
        if db.open:
            db.close()


class connect:

    """ Database Connection Class """

    def __init__(
        self, host: str = None, username: str = None, passwd: str = None,
        database: str = None, ssl: bool = False, ssl_ca: str = None,
        ssl_cert: str = None, ssl_key: str = None, connect_timeout: int = 10
    ):

        """ MySQL Database Connection

        Connects to the a MySQL database using the supplied configuration.

            ddi_db = clintosaurous.db.connect()

        Almost all options can be set by passing parameters to the function,
        CLI options, and Clintosaurous configuration file. Values are set in
        the database section of the configuration file. Remember to change
        from underscores to dashes in configuration file.

        Check order for a value is:
            1.  CLI option.
            2.  Function variable.
            3.  Clintosaurous configuration file.

        Paremeters:

        host (str): Database server DNS name or IP.
        username (str): Username for connecting to the database.
        passwd (str): Password for above username.
        database (str): Name of the database to use.
        ssl (bool): Enable/disable MySQL connection encryption.
        ssl_ca (str): Path to the SSL connection CA certification.
        ssl_cert (str): Path to SSL certificate to use for connection.
            See --db_ssl_cert CLI option help. This is not necessary if
            you are not doing SSL certifiate verification.
        ssl_key (str): Path to SSL key to use for connection. This is
            required if ssl_cert is specified.
        connect_timeout (int): Connection timeout in seconds.

        Return:

        Database connection object.

        Raises:

        TypeError: `host` not a str.
        TypeError: `username` not a str.
        TypeError: `passwd` not a str.
        TypeError: `database` not a str.
        TypeError: `ssl` not a bool.
        TypeError: `ssl_ca` not a str.
        TypeError: `ssl_cert` not a str.
        TypeError: `ssl_key` not a str.
        TypeError: `connect_timeout` not an int.
        """

        # Type hints.
        if host is not None and not isinstance(host, str):
            raise TypeError(f'`host` expected `str`, received {type(host)}')
        if username is not None and not isinstance(username, str):
            raise TypeError(
                f'`username` expected `str`, received {type(username)}')
        if passwd is not None and not isinstance(passwd, str):
            raise TypeError(
                f'`passwd` expected `str`, received {type(passwd)}')
        if database is not None and not isinstance(database, str):
            raise TypeError(
                f'`database` expected `str`, received {type(database)}')
        if not isinstance(ssl, bool):
            raise TypeError(f'`ssl` expected `bool`, received {type(ssl)}')
        if ssl_ca is not None and not isinstance(ssl_ca, str):
            raise TypeError(
                f'`ssl_ca` expected `str`, received {type(ssl_ca)}')
        if ssl_cert is not None and not isinstance(ssl_cert, str):
            raise TypeError(
                f'`ssl_cert` expected `str`, received {type(ssl_cert)}')
        if ssl_key is not None and not isinstance(ssl_key, str):
            raise TypeError(
                f'`ssl_key` expected `str`, received {type(ssl_key)}')
        if not isinstance(connect_timeout, int):
            raise TypeError(
                '`connect_timeout` expected `int`, ' +
                f'received {type(connect_timeout)}'
            )

        dbg_prefix = 'clintosaurous.mysql.connect()'

        # Read CLI arguments.
        opts = clintosaurous.opts.cli()
        # Read configuration file.
        conf = clintosaurous.file.conf()

        # Configuration file database settings.
        if 'database' in conf:
            db_conf = conf["database"]
        else:
            db_conf = {}

        # Verify database values parameters are set.
        self.options = {}
        options = [
            # name, passed, cli, required, default
            ["host", host, opts.db_host, True, None],
            ["database", database, opts.db_name, True, None],
            ["username", username, opts.db_username, True, None],
            ["passwd", passwd, opts.db_passwd, True, None],
            ["ssl", ssl, opts.db_ssl, False, False],
            ["ssl-ca", ssl_ca, opts.db_ssl_ca, False, None],
            ["ssl-cert", ssl_cert, opts.db_ssl_cert, False, None],
            ["ssl-key", ssl_key, opts.db_ssl_key, False, None],
            ["connect-timeout", connect_timeout, None, True, None]
        ]
        self._check_opts(options, db_conf)

        self.options["connection-timeout"] = connect_timeout

        if re.match(r'\\+`', self.options["passwd"]):
            cmd = re.sub(r'^\\+`|`$', '', self.options["passwd"])
            self.options["passwd"] = os.popen(cmd).read()

        self.connect_opts = {
            "host": self.options["host"],
            "user": self.options["username"],
            "password": self.options["passwd"],
            "database": self.options["database"],
            "connect_timeout": self.options["connect-timeout"]
        }
        if self.options["ssl"]:
            self.connect_opts["ssl"] = {"ssl": {
                "ca": self.options["ssl-ca"],
                "cert": self.options["ssl-cert"],
                "key": self.options["ssl-key"]
            }}

        log.log(
            f'Connecting to database {self.options["username"]}@' +
            f'{self.options["host"]}/{self.options["database"]}'
        )
        for key in self.connect_opts:
            if key in ['passwd', 'password']:
                disp = '*****'
            else:
                disp = self.connect_opts[key]
            log.dbg(f'{dbg_prefix}: self.connect_opts[{key}]: {disp}')

        self.connection = pymysql.connect(**self.connect_opts)
        self.commit = self.connection.commit
        self.cursor = self.connection.cursor
        self.DictCursor = pymysql.cursors.DictCursor
        self.pymysql = pymysql
        _connections.append(self.connection)

    def _check_opts(self, options: list[list], conf: dict) -> None:

        """
        Set connection option values for connecting to database.

        Internal only function and should not be called directly.

        `options` is the list of options to validate values for. Each element
        in the list is a list of option values:

            [name, user_passed, cli_opt, required, default_value]

        `name`: The configuration option name. i.e. 'user' for the database
        username.

        `user_passed`: The value supplied by the user.

        `cli_opt`: The CLI argument value.

        `required`: Boolean if the option is required. If a value is required
        and not supplied, a ValueError will be raised.

        `default_value`: The default value if not set elsewhere.

        Parameters:

        options (list[list]): List of lists of options to validate.
        conf (dict): Configuration file setttings.

        Raises:

        TypeError: options not a list.
        TypeError: conf not a dict.
        ValueError: If a required option value does not exist.
        """

        # Type hints.
        if not isinstance(options, list):
            raise TypeError(
                f'`options` expected `list`, received {type(options)}')
        if not isinstance(conf, dict):
            raise TypeError(f'`conf` expected `dict`, received {type(conf)}')

        for name, passed, cli, required, default in options:
            # Type hints for the required elements in the list.
            if not isinstance(name, str):
                raise TypeError(
                    f'Database option `{name}` expected `str`, ' +
                    f'received {type(name)}'
                )
            if required is not None and not isinstance(required, bool):
                raise TypeError(
                    f'Database option `{name}` required ' +
                    f'expected `bool`, received {type(required)}'
                )

            # Always prefer a CLI supplied value.
            if cli is not None:
                self.options[name] = cli
                continue

            # Prefer script supplied data next.
            elif passed is not None:
                self.options[name] = passed
                continue

            # Use configuration file.
            elif name in conf:
                self.options[name] = conf[name]
                continue

            # Raise a ValueError if required parameter and not supplied.
            elif required:
                raise ValueError(f'Database option `{name}` not supplied')

            # Otherwise, use the default.
            else:
                self.options[name] = default

    def close(self) -> None:

        """ Close Database Connection

        Closes the database connection and disconnects from the MySQL server.

            db.close()
        """

        log.log(
            f'Disconnecting from database {self.options["username"]}@' +
            f'{self.options["host"]}/{self.options["database"]}'
        )
        self.connection.close()


# Register to run commands on exit.
atexit.register(_atexit)
