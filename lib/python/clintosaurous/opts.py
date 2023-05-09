#!/opt/clintosaurous/venv/bin/python3 -Bu

""" CLI Argument Processing Module

This module provides CLI argument parsing functionality for Clintosaurous
tools scripts.

This is intended as an internal module for the Clintosaurous tools.

See `argparse` documention for details on parser syntax and usage.

https://docs.python.org/3/library/argparse.html

    clintosaurous.opts.parser
    argparse_parser = clintosaurous.opts.parser
    opts = clintosaurous.opts.cli()

`argparse` parser object for adding script specific options.
"""


import argparse
import sys


VERSION = '1.0.0'
LAST_UPDATE = '2023-01-08'


# Parser object for calling scripts to use.
parser = argparse.ArgumentParser()
# Previously parsed information.
_cli_opts = None
_uknown_args = None


def cli(known: bool = False, reparse: bool = False) -> argparse.Namespace:

    """ CLI Argument Parsing

    Parse the CLI options from the arguments passed on the CLI.

        opts = clintosaurous.opts.cli()
        opts, remaining = clintosaurous.opts.cli(known=True)

    Parameters:

    known (bool): Parse only known arguments. This causes argparse to return
        unparsed arguments or options it doesn't know. Default: False
    reparse (bool): Force cli() to reparse CLI options. By default, it only
        reads them once and returns the cached results on subsequent calls.

    Return:

    argparse.Namespace: `argparse.Namespace` object of parsed CLI options.
    list: Only returned if `known` is `True`. A list of arguments remaining
        after options are parsed.

    Raises:

    TypeError: `known` not a `bool`.
    TypeError: `reparse` not a `bool`.
    """

    if not isinstance(known, bool):
        raise TypeError(f'`known` expected `bool`, received {type(known)}')
    if not isinstance(reparse, bool):
        raise TypeError(
            f'`reparse` expected `bool`, received {type(reparse)}')

    # Use global variables for storing and retrieving data.
    global _cli_opts
    global parser
    global _uknown_args

    # If reparsing the CLI options, clear persistent data variables.
    if reparse:
        _cli_opts = None
        _uknown_args = None

    # If CLI arguments previously parsed, return those results.
    if _cli_opts:
        if known:
            return _cli_opts, _uknown_args
        return _cli_opts

    # `sys.argv[0]` by default will be the script name. If you specify
    # `sys.argv` in `parser.parse_args()`, it will try to parse the script
    # name as an argument to the script. This causes `parser.parse_args()` to
    # fail. Strip off the script name to work around this. Copy `sys.argv` to
    # preserve original values.
    orig_args = sys.argv.copy()
    del orig_args[0]

    # If `known` set, parse only known CLI arguments.
    if known:
        _cli_opts, _uknown_args = parser.parse_known_args(orig_args)
        return _cli_opts, _uknown_args

    # Parse all CLI arguments. If a CLI argument is unknown, `arparse` will
    # throw an exception.
    else:
        _cli_opts = parser.parse_args(orig_args)
        return _cli_opts
