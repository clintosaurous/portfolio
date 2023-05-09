#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
Functions for SNMP services.
"""


import dns.resolver as pyresolv
from ipaddress import ip_address
import clintosaurous.opts
from pysnmp.hlapi import *
import re


VERSION = '1.1.3'
LAST_UPDATE = '2022-11-19'


# CLI options.
_parser_log_group = clintosaurous.opts.parser.add_argument_group('SNMP')

_parser_log_group.add_argument(
    '-C', '--snmp_community',
    help='Set default SNMP community string.',
    type=str
)
_parser_log_group.add_argument(
    '-H', '--snmp_host',
    help='Set default SNMP host to query.',
    type=str
)
_parser_log_group.add_argument(
    '-t', '--snmp_timeout',
    help='Set default SNMP query timeout.',
    type=int,
    default=10
)
_parser_log_group.add_argument(
    '-r', '--snmp_retry',
    help="""
        Set default SNMP query retry count. This is in addition to the first
        query.
    """,
    type=int,
    default=1
)


class SNMPError(Exception):

    """
    SNMP error exception.
    """

    pass


def _snmp_resp_value(r_value):

    """
    Converted SNMP data types to standard data types.
    """

    if (
        isinstance(r_value.subtype(), Integer)
        or isinstance(r_value.subtype(), TimeTicks)
    ):
        return int(r_value)
    elif isinstance(r_value.subtype(), IpAddress):
        return '.'.join([str(o) for o in r_value.asNumbers()])
    else:
        return str(r_value)


class sesssion:

    """
    Create an SNMP session object for SNMP calls to a host.
    """

    def __init__(
        self, host: str = None, community: str = None, timeout: int = None,
        retry: int = None
    ):

        # Type hints.
        if host and not isinstance(host, str):
            raise TypeError(f'host expected `str`, received {type(host)}')
        if community and not isinstance(community, str):
            raise TypeError(
                f'community expected `str`, received {type(community)}')
        if timeout and not isinstance(timeout, int):
            raise TypeError(
                f'timeout expected `int`, received {type(timeout)}')
        if retry and not isinstance(retry, int):
            raise TypeError(f'retry expected `int`, received {type(retry)}')

        self.opts = clintosaurous.opts.cli()

        if host:
            self.host = host
        elif self.opts.snmp_host:
            self.host = self.opts.snmp_host
        else:
            raise SNMPError('SNMP host missing')

        try:
            self.ip = str(ip_address(self.host))
        except ValueError:
            try:
                self.ip = str(pyresolv.query(self.host)[0])
            except (
                pyresolv.LifetimeTimeout,
                pyresolv.NoNameservers,
                pyresolv.NXDOMAIN
            ):
                raise SNMPError(f'{host} does not resolve in DNS')

        if re.match(r'127\.|::', self.ip):
            raise SNMPError(f'Cannot use localhost IP addresses')

        if community:
            self.community = community
        elif self.opts.snmp_community:
            self.community = self.opts.snmp_community
        else:
            raise SNMPError('SNMP community string missing')

        if timeout:
            self.timeout = timeout
        else:
            self.timeout = self.opts.snmp_timeout
        if retry:
            self.retry = retry
        else:
            self.retry = self.opts.snmp_retry

        self.oids = self.oids()

    def bulk(
        self, oid: str, timeout: int = None, retry: int = None
    ) -> list[tuple]:

        """
        Perform SNMP subtree query for the OID supplied.
        """

        # Type hints.
        if not isinstance(oid, str):
            raise TypeError(f'oid expected `str`, received {type(oid)}')
        if timeout and not isinstance(timeout, int):
            raise TypeError(
                f'timeout expected `int`, received {type(timeout)}')
        if retry and not isinstance(retry, int):
            raise TypeError(f'retry expected `int`, received {type(retry)}')

        if not timeout:
            timeout = self.timeout
        if not retry:
            retry = self.retry

        bulk_return = bulkCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip, 161)),
            ContextData(),
            0, 25,
            ObjectType(ObjectIdentity(oid))
        )

        oid = re.sub(r'^\.', '', oid)
        reg_oid = oid.replace('.', '\.')
        orig_reg = re.compile(reg_oid + r'\.')
        return_data = []
        end = False

        for error_ind, error_stat, errorIndex, varbinds in bulk_return:
            if error_ind:
                if str(error_stat) != 'noError':
                    raise SNMPError(f'{self.ip}: {error_ind}')
                break

            for r_oid, r_value in varbinds:
                r_oid = str(r_oid)
                if not orig_reg.match(r_oid):
                    end = True
                    break
                return_data.append((r_oid, _snmp_resp_value(r_value)))

            if end:
                break

        return return_data

    def get(self, oid: str, timeout: int = None, retry: int = None):

        """
        Perform SNMP get against supplied list of OIDs.
        """

        # Type hints.
        if not isinstance(oid, str):
            raise TypeError(f'oid expected `str`, received {type(oid)}')
        if timeout and not isinstance(timeout, int):
            raise TypeError(
                f'timeout expected `int`, received {type(timeout)}')
        if retry and not isinstance(retry, int):
            raise TypeError(f'retry expected `int`, received {type(retry)}')

        if not timeout:
            timeout = self.timeout
        if not retry:
            retry = self.retry

        get_return = getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        error_ind, error_stat, errorIndex, varbinds = next(get_return)
        if error_ind:
            raise SNMPError(f'{self.ip}: {error_ind}')

        return _snmp_resp_value(varbinds[0][1])

    def sysDescr(self) -> str:

        """
        Query sysLocation.
        """

        return self.get(self.oids.sysDescr, timeout=2)

    def sysLocation(self) -> str:

        """
        Query sysLocation.
        """

        return self.get(self.oids.sysLocation, timeout=2)

    def sysName(self) -> str:

        """
        Query sysName.
        """

        return self.get(self.oids.sysName, timeout=2)

    def sysObjectID(self) -> str:

        """
        Query sysObjectID.
        """

        return self.get(self.oids.sysObjectID, timeout=2)

    class oids:

        """
        Commonly used SNMP MIB OIDs.
        """

        def __init__(self):

            self.sysDescr = '.1.3.6.1.2.1.1.1.0'
            self.sysObjectID = '.1.3.6.1.2.1.1.2.0'
            self.sysName = '.1.3.6.1.2.1.1.5.0'
            self.sysLocation = '.1.3.6.1.2.1.1.6.0'

            self.ifEntry = '.1.3.6.1.2.1.2.2.1'
            self.ifDescr = '.1.3.6.1.2.1.2.2.1.2'
            self.ifAdminStatus = '.1.3.6.1.2.1.2.2.1.7'
            self.ifOperStatus = '.1.3.6.1.2.1.2.2.1.8'

            self.ifName = '.1.3.6.1.2.1.31.1.1.1.1'
            self.ifAlias = '.1.3.6.1.2.1.31.1.1.1.18'

            self.private = '.1.3.6.1.4'
