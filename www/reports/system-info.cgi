#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
Displays summary of host specific information.
"""


import clintosaurous.cgi
import clintosaurous.credentials as credentials
from clintosaurous.datetime import run_time, time_breakdown
import clintosaurous.db
import ipaddress
import re


VERSION = '1.2.0'
LAST_UPDATE = '2022-10-28'


def bytedown(byte_cnt: int) -> str:

    """
    Converts the number of bytes to human readable format.
    """

    # Type hints.
    if not isinstance(byte_cnt, int):
        raise TypeError(f'byte_cnt expected `int`, received {type(byte_cnt)}')

    if byte_cnt < 1024:
        return str(byte_cnt) + 'B'
    byte_cnt /= 1024
    if byte_cnt < 1024:
        return str(round(byte_cnt, 2)) + 'KB'
    byte_cnt /= 1024
    if byte_cnt < 1024:
        return str(round(byte_cnt, 2)) + 'MB'
    byte_cnt /= 1024
    if byte_cnt < 1024:
        return str(round(byte_cnt, 2)) + 'GB'
    byte_cnt /= 1024
    return str(round(byte_cnt, 2)) + 'TB'

# End: bytedown()


def disp_host(db: clintosaurous.db.connect, host: str) -> None:

    """
    Display host specific information.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')
    if not isinstance(host, str):
        raise TypeError(f'host expected `str`, received {type(host)}')

    device_data = query_device(db, host)
    disk_data = query_disk(db, host)
    memory_data = query_memory(db, host)
    network_data = query_network(db, host)

    title = f'{host} -'

    main_table_rows = []

    # Device information.

    sub_table_rows = []
    if device_data["sysname"] is not None:
        sub_table_rows.append(["sysName:", device_data["sysname"]])
    if device_data["ip"]:
        mgt_ip = ipaddress.ip_address(device_data["ip"])
        sub_table_rows.append(["Management IP:", mgt_ip])
    if device_data["features"] is not None:
        os_ver = device_data["features"]
        if device_data["version"] is not None:
            os_ver += f' ({device_data["version"]})'
        sub_table_rows.append(["OS Version:", os_ver])
    if device_data["uptime"] is not None:
        sub_table_rows.append(["Uptime:", run_time(device_data["uptime"])])
    sub_table_rows.append(["Date Added:", device_data["added"]])
    if device_data["last_discovered"] is not None:
        sub_table_rows.append([
            "Last Discovered:",device_data["last_discovered"]])
    sub_table_rows.append(["Last Polled:", device_data["last_polled"]])
    if device_data["contact"] is not None:
        sub_table_rows.append(["Contact:", device_data["contact"]])
    if device_data["location"] is not None:
        sub_table_rows.append(["Location:", device_data["location"]])
    main_table_rows.append([
        "Device:",
        cgi.table(sub_table_rows, headings=False)
    ])

    # Hardware information.
    sub_table_rows = []
    if device_data["hardware"] is not None:
        sub_table_rows.append(["Model:", device_data["hardware"]])
    if device_data["serial"] is not None:
        sub_table_rows.append(["Serial Number:", device_data["serial"]])
    if memory_data:
        sub_table_rows.append(["Memory:", bytedown(memory_data["total"])])
    if device_data["proc_type"] is not None:
        sub_table_rows.append(["Processor:", device_data["proc_type"]])
        sub_table_rows.append(["Processor Count:", device_data["proc_count"]])

    if sub_table_rows:
        main_table_rows.append([
            "Hardware:",
            cgi.table(sub_table_rows, headings=False)
        ])

    # Memory information.
    if memory_data:
        freep = round(memory_data["free"] / memory_data["total"] * 100, 1)
        free = f'{bytedown(memory_data["free"])} ({freep}%)'
        usedp = round(memory_data["used"] / memory_data["total"] * 100, 1)
        used = f'{bytedown(memory_data["used"])} ({usedp}%)'
        sub_table_rows = [
            ["Total:", bytedown(memory_data["total"])],
            ["Used:", used],
            ["Free:", free]
        ]
        main_table_rows.append([
            "Memory:",
            cgi.table(sub_table_rows, headings=False)
        ])

    # Network information.
    if network_data:
        sub_table_rows = []
        for int_name in sorted(network_data.keys()):
            int_data = network_data[int_name]
            if 'ip' not in int_data:
                continue

            int_sub_table = []
            if int_data["model"] is not None:
                int_sub_table.append(["Model:", int_data["model"]])
            if int_data["mac"] is not None:
                mac = re.sub(
                    r'(\w{4})(\w{4})(\w{4})', r'\1.\2.\3', int_data["mac"]
                ).lower()
                int_sub_table.append(["MAC:", mac])

            ip_list = []
            if 'ip' in int_data:
                for ip_ver in sorted(int_data["ip"].keys()):
                    for ip in sorted(int_data["ip"][ip_ver]):
                        ip_list.append(ip.lower())
                int_sub_table.append(["IP Addresses:", "<br>".join(ip_list)])

            if int_sub_table:
                sub_table_rows.append([
                    f'{int_name}:', cgi.table(int_sub_table, headings=False)])

        if sub_table_rows:
            main_table_rows.append([
                "Network:", cgi.table(sub_table_rows, headings=False)])

    # Disk information.
    if disk_data:
        sub_table_rows = []
        for disk in sorted(disk_data.keys()):
            disk_info = disk_data[disk]
            freep = round(disk_info["free"] / disk_info["size"] * 100, 1)
            free = f'{bytedown(disk_info["free"])} ({freep}%)'
            usedp = round(disk_info["used"] / disk_info["size"] * 100, 1)
            used = f'{bytedown(disk_info["used"])} ({usedp}%)'
            disk_table_rows = [
                ["Size:", bytedown(disk_info["size"])],
                ["Used:", used],
                ["Free:", free]
            ]
            sub_table_rows.append([
                disk,
                cgi.table(disk_table_rows, headings=False)
            ])

        main_table_rows.append([
            "Disk:", cgi.table(sub_table_rows, headings=False)])

    print(cgi.text_box(cgi.table(main_table_rows, headings=False), title))

# End: disp_hosts(dev_data)


def disp_host_list(db: clintosaurous.db.connect) -> None:

    """
    Display all hosts summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    dev_data = {}

    sql = """
        select distinct
            case
                when d.display is not null then d.display
                else d.hostname
            end as hostname,
            m.mempool_total,
            m.mempool_free,
            p.proc_count,
            d.uptime

        from librenms.devices as d

        left join librenms.mempools as m
            on m.device_id = d.device_id
            and m.mempool_class = 'system'

        left join (
            select p1.device_id, count(p1.hrDeviceDescr) as proc_count
            from librenms.hrDevice as p1
            where p1.hrDeviceType = 'hrDeviceProcessor'
            group by p1.device_id
        ) as p
            on p.device_id = d.device_id
    """
    cursor = db.cursor(db.DictCursor)
    cursor.execute(sql)

    for row in cursor:
        new_row = {"disks": []}
        for key in row.keys():
            new_row[key] = row[key]
        dev_data[row["hostname"]] = new_row

    cursor.close()

    sql = """
        select
            case
                when d.display is not null then d.display
                else d.hostname
            end as hostname,
            case
                when s.storage_descr =
                    '/vmfs/volumes/5c967394-50c29e43-8f29-0026557d1e0a'
                    then '/datastore1'
                else s.storage_descr
            end as storage_descr,
            s.storage_size,
            s.storage_free
        from librenms.storage as s
        inner join librenms.devices as d
            on d.device_id = s.device_id
        where
            s.storage_type in ('dsk', 'hrStorageFixedDisk')
            and s.storage_descr != '/boot'
            and s.storage_descr not like '/boot/%%'
            and s.storage_descr not like '/dev/%%'
            and s.storage_descr != '/run'
            and s.storage_descr not like '/run/%%'
            and s.storage_descr not like '/srv/%%'
            and s.storage_descr not like '/sys/%%'
            and s.storage_descr not like '/var/%%'
        order by
            hostname,
            s.storage_descr
    """
    cursor = db.cursor(db.DictCursor)
    cursor.execute(sql)

    for row in cursor:
        new_row = {}
        for key in row.keys():
            new_row[key] = row[key]
        dev_data[row["hostname"]]["disks"].append(new_row)

    cursor.close()

    table_rows = [[
        'Hostname', 'Mem Total', 'Mem Free', '%', 'Procs',
        'Disk', 'Size', 'Free', '%', 'Uptime'
    ]]

    for hostname in sorted(dev_data.keys()):
        host = dev_data[hostname]
        disks = host["disks"]
        host_url = (
            f'<a class="host_link" href="?host={host["hostname"]}">' +
            f'{host["hostname"]}</a>'
        )

        if host["mempool_total"] is not None:
            mem_total = \
                f'<div class="rjust">{bytedown(host["mempool_total"])}</div'
            mem_free = \
                f'<div class="rjust">{bytedown(host["mempool_free"])}</div>'
            percent = \
                round(host["mempool_free"] / host["mempool_total"] * 100, 2)
            mem_free_percent = f'<div class="rjust">{percent}</div>%'
        else:
            mem_total = ''
            mem_free = ''
            mem_free_percent = ''

        if host["proc_count"] is not None:
            proc_count = f'<div class="rjust">{host["proc_count"]}</div>'
        else:
            proc_count = ''

        if host["uptime"] is not None:
            uptimes = time_breakdown(host["uptime"])
            up_section = []
            if uptimes[0]:
                up_section.append(f'{uptimes[0]}d')
            if uptimes[1]:
                up_section.append(f'{uptimes[1]}h')
            if uptimes[2]:
                up_section.append(f'{uptimes[2]}m')
            if uptimes[3]:
                up_section.append(f'{uptimes[3]}s')
            uptime = ', '.join(up_section)
        else:
            uptime = ''

        if disks:
            prev_host = False

            for row in disks:
                if prev_host and prev_host == row["hostname"]:
                    host_url = ''
                    mem_total = ''
                    mem_free = ''
                    mem_free_percent = ''
                    proc_count = ''
                    uptime = ''
                prev_host = row["hostname"]
                disk_size = (
                    f'<div class="rjust">{bytedown(row["storage_size"])}' +
                    '</div>'
                )
                disk_free = (
                    f'<div class="rjust">{bytedown(row["storage_free"])}' +
                    '</div>'
                )
                percent = \
                    round(row["storage_free"] / row["storage_size"] * 100, 2)
                percent_free = f'<div class="rjust">{percent}</div>'
                table_rows.append([
                    host_url,
                    mem_total,
                    mem_free,
                    mem_free_percent,
                    proc_count,
                    row["storage_descr"],
                    disk_size,
                    disk_free,
                    percent_free,
                    uptime
                ])
        else:
            table_rows.append([
                host_url,
                mem_total,
                mem_free,
                mem_free_percent,
                proc_count,
                '',
                '',
                '',
                '',
                uptime
            ])

    cursor.close()

    print(cgi.text_box(cgi.table(table_rows)))

# End: disp_host_list()


def page_styles() -> None:

    """
    Script specific HTML style information.
    """

    print("""
        <style>
            a.host_link:link { text-decoration: none; }
            a.host_link:visited { text-decoration: none; }
            a.host_link:hover { text-decoration: none; }
            a.host_link:active { text-decoration: none; }
            table.data_table { width: 80%; }
            td.data_table_heading { white-space: nowrap; }
            td.data_table_data { width: 25%; white-space: nowrap; }
            div.rjust { text-align: right; }:
        </style>
    """)

# End page_styles()


def query_device(db: clintosaurous.db.connect, host: str) -> dict:

    """
    Query data for a specific host.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')
    if not isinstance(host, str):
        raise TypeError(f'host expected `str`, received {type(host)}')

    device_data = {}

    sql = """
        select
            d.sysName as sysname,
            d.inserted as added,
            case
                when d.display is not null then d.hostname
                else null
            end as ip,
            d.sysContact as contact,
            d.version,
            d.hardware,
            d.features,
            d.uptime,
            d.last_polled,
            d.serial,
            d.last_discovered,
            l.location
        from librenms.devices as d
        inner join librenms.locations as l
            on l.id = d.location_id
        where
            d.hostname = %s
            or d.display = %s
    """
    cursor = db.cursor(db.DictCursor)
    cursor.execute(sql, [host, host])
    row = cursor.fetchone()
    cursor.close()
    for key in row.keys():
        if row[key]:
            device_data[key] = row[key]
        else:
            device_data[key] = None

    sql = """
        select
            p.hrDeviceDescr as proc_type,
            count(p.hrDeviceDescr) as proc_count
        from librenms.devices as d
        inner join librenms.hrDevice as p
            on p.device_id = d.device_id
            and p.hrDeviceType = 'hrDeviceProcessor'
        where d.hostname = %s or d.display = %s
        group by p.hrDeviceDescr
    """
    cursor = db.cursor(db.DictCursor)
    cursor.execute(sql, [host, host])
    proc_type = None
    proc_count = 0
    for row in cursor:
        if proc_type is None:
            proc_type = re.sub(
                r'^GenuineIntel:\s+|^CPU Pkg\S+:\s+\S+\s+', '',
                row["proc_type"], re.I
            )
        proc_count += row["proc_count"]
    cursor.close()

    if proc_type is not None:
        device_data["proc_type"] = proc_type
        device_data["proc_count"] = proc_count
    else:
        device_data["proc_type"] = None
        device_data["proc_count"] = None

    return device_data

# End: query_device()


def query_disk(db: clintosaurous.db.connect, host: str) -> dict:

    """
    Query disk information for specific host.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')
    if not isinstance(host, str):
        raise TypeError(f'host expected `str`, received {type(host)}')

    sql = """
        select
            case
                when s.storage_descr =
                    '/vmfs/volumes/5c967394-50c29e43-8f29-0026557d1e0a'
                    then '/datastore1'
                else s.storage_descr
            end as disk,
            s.storage_size as size,
            s.storage_used as used,
            s.storage_free as free
        from librenms.storage as s
        inner join librenms.devices as d
            on d.device_id = s.device_id
            and (d.hostname = %s or d.display = %s)
        where
            s.storage_type in ('dsk', 'hrStorageFixedDisk')
            and s.storage_descr != '/boot'
            and s.storage_descr not like '/boot/%%'
            and s.storage_descr not like '/dev/%%'
            and s.storage_descr != '/run'
            and s.storage_descr not like '/run/%%'
            and s.storage_descr not like '/srv/%%'
            and s.storage_descr not like '/sys/%%'
            and s.storage_descr not like '/var/%%'
    """
    cursor = db.cursor(db.DictCursor)
    cursor.execute(sql, [host, host])

    disk_data = {}
    for row in cursor:
        disk_data[row["disk"]] = row

    cursor.close()

    return disk_data

# End: query_disk()


def query_memory(db: clintosaurous.db.connect, host: str) -> tuple:

    """
    Query memory information for specific host.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')
    if not isinstance(host, str):
        raise TypeError(f'host expected `str`, received {type(host)}')

    sql = """
        select distinct
            m.mempool_total as total,
            m.mempool_used as used,
            m.mempool_free as free
        from librenms.mempools as m
        inner join librenms.devices as d
            on d.device_id = m.device_id
            and (d.hostname = %s or d.display = %s)
            -- and d.hostname != 'bedroom-switch1'
        where
            m.mempool_class = 'system'
    """
    cursor = db.cursor(db.DictCursor)
    cursor.execute(sql, [host, host])
    memory_info = cursor.fetchone()
    cursor.close()

    return memory_info

# End: query_memory()


def query_network(db: clintosaurous.db.connect, host: str) -> dict:

    """
    Query network information for specific host.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')
    if not isinstance(host, str):
        raise TypeError(f'host expected `str`, received {type(host)}')

    network_data = {}

    sql = """
        select
            p.ifName as name,
            p.ifDescr as model,
            p.ifSpeed as speed,
            p.ifPhysAddress as mac
        from librenms.ports as p
        inner join librenms.devices as d
            on d.device_id = p.device_id
            and (d.hostname = %s or d.display = %s)
        where
            p.ifName not like 'lo%%'
            and p.ifOperStatus = 'up'
    """
    cursor = db.cursor(db.DictCursor)
    cursor.execute(sql, [host, host])
    for row in cursor:
        network_data[row["name"]] = row

    sql = """
        select distinct
            p4.ifName as interface,
            concat(i4.ipv4_address, '/', i4.ipv4_prefixlen) as ip_address,
            4 as ip_ver
        from librenms.ipv4_addresses as i4
        inner join librenms.ports as p4
            on p4.port_id = i4.port_id
            and p4.ifName not like 'lo%%'
            and p4.ifOperStatus = 'up'
        inner join librenms.devices as d4
            on d4.device_id = p4.device_id
            and (d4.hostname = %s or d4.display = %s)

        union

        select distinct
            p6.ifName as interface,
            concat(i6.ipv6_address, '/', i6.ipv6_prefixlen) as ip_address,
            6 as ip_ver
        from librenms.ipv6_addresses as i6
        inner join librenms.ports as p6
            on p6.port_id = i6.port_id
            and p6.ifName not like 'lo%%'
            and p6.ifOperStatus = 'up'
        inner join librenms.devices as d6
            on d6.device_id = p6.device_id
            and (d6.hostname = %s or d6.display = %s)
    """
    cursor = db.cursor(db.DictCursor)
    cursor.execute(sql, [host, host, host, host])

    for row in cursor:
        if row["interface"] in network_data:
            int_data = network_data[row["interface"]]
        else:
            continue

        if 'ip' in int_data:
            ip_data = int_data["ip"]
        else:
            int_data["ip"] = {}
            ip_data = int_data["ip"]

        if row["ip_ver"] not in ip_data:
            ip_data[row["ip_ver"]] = []

        ip_data[row["ip_ver"]].append(
            str(ipaddress.ip_interface(row["ip_address"])))

    cursor.close()

    return network_data

# End: query_network()


if __name__ == '__main__':
    cgi = clintosaurous.cgi.cgi(
        title='System Information',
        version=VERSION,
        last_update=LAST_UPDATE,
        copyright=2022
    )

    print(cgi.start_page())
    page_styles()

    user, passwd = credentials.data().get('mysql-report_ro')
    db = clintosaurous.db.connect(
        host='mysql1.clintosaurous.com',
        user=user,
        passwd=passwd,
        database='reports',
        logging=False
    )

    print(cgi.hr())
    if 'host' in cgi.form_values:
        disp_host(db, cgi.form_values["host"].value)
    else:
        disp_host_list(db)

    db.close()

    print(cgi.end_page())
