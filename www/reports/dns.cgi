#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
Display DNS report data from reports table.
"""


import clintosaurous.cgi
from clintosaurous.datetime import datestamp
import clintosaurous.ddi
import re
import time


VERSION = '2.1.0'
LAST_UPDATE = '2022-10-26'


def display_block_client(
    ddi: clintosaurous.ddi.connect, ddi_dev:  clintosaurous.ddi.connect
) -> None:

    """
    Display information for a specific client.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')
    if not isinstance(ddi_dev, clintosaurous.ddi.connect):
        raise TypeError(
            'db_dev expected `clintosaurous.ddi.connect`, ' +
            f'received {type(ddi_dev)}'
        )

    sql = "select distinct zone, block_type from ddi_block_zones"

    block_zones = {}
    for db in [ddi.db, ddi_dev.db]:
        cursor = db.cursor()
        cursor.execute(sql)
        for db_row in cursor:
            row = list(db_row)
            row[1] = re.sub(
                r'^( [a-z])\1',
                lambda pat: pat.group(1).capitalize(),
                row[1]
            )
            block_zones[row[0]] = row[1]
        cursor.close()

    client = cgi.form_values.getvalue("client")

    sql = """
        select
            query_timestamp,
            dns_request

        from ddi_dns_query_log

        where
            query_timestamp between %s and %s
            and query_host = %s
            and dns_request not like '%%.clintosaurous.home.'
            and dns_request not like '%%.clintosaurous.com.'
            and dns_request not like '%%.168.192.in-addr.arpa.'
    """

    rpt_rows = []

    for db in [ddi.db, ddi_dev.db]:
        cursor = db.cursor()
        cursor.execute(sql, [start_time, end_time, client])
        for db_row in cursor:
            row = list(db_row)
            row[1] = re.sub(r'\.$', '', row[1])
            dns_request = row[1]
            while re.search(r'\.', dns_request):
                try:
                    block_zones[dns_request]
                except KeyError:
                    dns_request = re.sub(r'^[^\.]+\.', '', dns_request)
                    continue
                rpt_rows.append([
                    row[0], row[1], dns_request, block_zones[dns_request]
                ])
                break

    rpt_rows = sorted(rpt_rows, key=lambda r: r[0])
    rpt_rows.reverse()
    rpt_rows.insert(
        0, ['Query Time', 'DNS Request', 'Block Zone', 'Block Type'])

    title = f'Ad/Malware Blocked Requests for {client} on {rpt_date}.'

    table_html = \
        f'<p>{len(rpt_rows) - 1} requests found.</p>\n' + cgi.table(rpt_rows)
    print(cgi.hr())
    print(cgi.text_box(title, table_html))

# End: display_block_client()


def display_client_requests(
    ddi: clintosaurous.ddi.connect, ddi_dev:  clintosaurous.ddi.connect
):

    """
    Display specific client requests.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')
    if not isinstance(ddi_dev, clintosaurous.ddi.connect):
        raise TypeError(
            'db_dev expected `clintosaurous.ddi.connect`, ' +
            f'received {type(ddi_dev)}'
        )

    client = cgi.form_values.getvalue("client")

    sql = """
        select
            query_timestamp,
            lower(dns_request),
            server_name

        from ddi_dns_query_log

        where
            query_timestamp between %s and %s
            and client_ip = %s

        order by
            query_timestamp desc
    """

    for db in [ddi.db, ddi_dev.db]:
        cursor = db.cursor()
        cursor.execute(sql, [start_time, end_time, client])
        rpt_rows = [[list(r)] for r in cursor]
        cursor.close()

    rpt_rows.insert(0, [
        'DNS Request Time',
        'DNS Request',
        'DNS Server'
    ])

    title = f'DNS Requests for {client} on {rpt_date}.'
    table_html = \
        f'<p>{len(rpt_rows) - 1} requests found.</p>\n' + cgi.table(rpt_rows)

    print(cgi.hr())
    print(cgi.text_box(title, table_html))

# End: display_client_requests()


def display_report(ddi: clintosaurous.ddi.connect):

    """
    Display summary reports.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')

    sql = """
        select sum(count)
        from reports.dns_queries_per_server
        where datestamp = %s
    """
    cursor = ddi.db.cursor()
    cursor.execute(sql, [rpt_date])
    query_total = f'{int(cursor.fetchone()[0]):,}'
    cursor.close()

    html = f'<p>Total Queries: {query_total}</p>\n'
    print(cgi.hr())
    print(cgi.text_box(f'Query Counts for {rpt_date}', html))

    title = "Queries Per Server"
    rows = rpt_per_server(ddi)
    print(cgi.hr())
    print(cgi.text_box(title, cgi.table(rows)))

    title = "Queries Per Client"
    rows = rpt_per_client(ddi)
    print(cgi.hr())
    print(cgi.text_box(title, cgi.table(rows)))

    title = "Top Client DNS Queries"
    rows = rpt_top_queries(ddi)
    print(cgi.hr())
    print(cgi.text_box(title, cgi.table(rows)))

    title = "Top Queried Domains"
    rows = rpt_top_domains(ddi)
    print(cgi.hr())
    print(cgi.text_box(title, cgi.table(rows)))

    title = "clintosaurous.com Query Counts"
    rows = rpt_clint_home(ddi)
    print(cgi.hr())
    print(cgi.text_box(title, cgi.table(rows)))

    title = "Ad/Malware Block Host Queries"
    rows = rpt_ad_block_hosts(ddi)
    print(cgi.hr())
    print(cgi.text_box(title, cgi.table(rows)))

    title = "Ad/Malware Block Zone Counts"
    rows = rpt_ad_block_zones(ddi)
    print(cgi.hr())
    print(cgi.text_box(title, cgi.table(rows)))

# End: display_report()


def rpt_ad_block_hosts(ddi: clintosaurous.ddi.connect) -> list:

    """
    Ad block hosts summary.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'ddi expected `clintosaurous.ddi.connect`, received {type(ddi)}')
    if not isinstance(ddi_dev, clintosaurous.ddi.connect):
        raise TypeError(
            'db ddi_dev `clintosaurous.ddi.connect`, ' +
            f'received {type(ddi_dev)}'
        )

    sql = """
        select client, count, concat(percentage, '%%')
        from reports.dns_ad_malware_hosts
        where datestamp = %s
        order by count desc
    """
    count = 0
    rpt_rows = [['Client', 'Count', 'Percentage']]

    cursor = ddi.db.cursor()
    cursor.execute(sql, [rpt_date])
    for db_row in cursor:
        row = list(db_row)
        count += 1

        row[1] = f'{row[1]:,}'
        row.append("""
            <form method="put" action=""
                enctype="multipart/form-data" name="ad_host{}">
            <input type="hidden" name="date" value="{}" />
            <input type="hidden" name="client" value="{}" />
            <input type="submit" name="client_block" value="View" />
            </form>
        """.format(count, rpt_date, row[0]))
        rpt_rows.append(row)

    cursor.close()

    return rpt_rows

# End: rpt_ad_block_hosts()


def rpt_ad_block_zones(ddi: clintosaurous.ddi.connect) -> list:

    """
    Ad block zones summary.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')

    sql = """
        select zone, zone_type, count, concat(percentage, '%%')
        from reports.dns_ad_malware_queries
        where datestamp = %s
        order by count desc
    """
    cursor = ddi.db.cursor()
    cursor.execute(sql, [rpt_date])

    rpt_rows = [['Ad/Malware Zone', 'Zone Type', 'Count', 'Percentage']]
    for db_row in cursor:
        row = list(db_row)
        row[2] = f'{row[2]:,}'
        rpt_rows.append(row)

    cursor.close()

    return rpt_rows

# End: rpt_ad_block_zones()


def rpt_clint_home(ddi: clintosaurous.ddi.connect) -> list:

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')

    sql = """
        select dns_name, count, concat(percentage, '%%')
        from reports.dns_clint_home_query_hosts
        where datestamp = %s
        order by count desc
    """
    cursor = ddi.db.cursor()
    cursor.execute(sql, [rpt_date])

    rpt_rows = [['DNS Query', 'Count', 'Percentage']]
    for db_row in cursor:
        row = list(db_row)
        row[1] = f'{row[1]:,}'
        rpt_rows.append(row)

    cursor.close()

    return rpt_rows

# End: rpt_clint_home()


def rpt_form_options(ddi: clintosaurous.ddi.connect) -> dict:

    """
    Generate report form options.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')

    sql = """
        select distinct datestamp
        from reports.dns_queries_per_server
        order by datestamp desc
    """
    cursor = ddi.db.cursor()
    cursor.execute(sql)
    dates = [str(b[0]) for b in cursor]
    cursor.close()

    params = {
        "method": 'put',
        "fields": [
            {
                "type": 'dropdown',
                "title": 'Date',
                "name": 'date',
                "values": dates,
                "default": dates[0]
            }
        ],
        "buttons": [{"name": 'submit_view', "value": 'View'}]
    }

    return params

# End: rpt_form_options()


def rpt_per_client(ddi: clintosaurous.ddi.connect) -> list:

    """
    Per client query counts summary report.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')

    sql = """
        select client, count, concat(percentage, '%%')
        from reports.dns_queries_per_client
        where datestamp = %s
        order by count desc
    """
    cursor = ddi.db.cursor()
    cursor.execute(sql, [rpt_date])

    count = 0
    rpt_rows = [['Client', 'Count', 'Percentage']]
    for db_row in cursor:
        row = list(db_row)
        count += 1
        row[1] = f'{row[1]:,}'

        row.append("""
            <form method="put" action=""
                enctype="multipart/form-data" name="ad_host{}">
            <input type="hidden" name="date" value="{}" />
            <input type="hidden" name="client" value="{}" />
            <input type="submit" name="client_requests" value="View" />
            </form>
        """.format(count, rpt_date, row[0]))

        rpt_rows.append(row)

    return rpt_rows

# End: rpt_per_client()


def rpt_per_server(ddi: clintosaurous.ddi.connect) -> list:

    """
    Per server query counts summary report.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')

    sql = """
        select host, count, concat(percentage, '%%')
        from reports.dns_queries_per_server
        where datestamp = %s
        order by count desc
    """
    cursor = ddi.db.cursor()
    cursor.execute(sql, [rpt_date])

    rpt_rows = [['Host', 'Count', 'Percentage']]
    for db_row in cursor:
        row = list(db_row)
        row[1] = f'{row[1]:,}'
        rpt_rows.append(row)

    return rpt_rows

# End: rpt_per_server()


def rpt_top_domains(ddi: clintosaurous.ddi.connect) -> list:

    """
    Per domain query counts summary report.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')

    sql = """
        select domain, count, concat(percentage, '%%')
        from reports.dns_top_queried_domains
        where datestamp = %s
        order by count desc
        limit 50
    """
    cursor = ddi.db.cursor()
    cursor.execute(sql, [rpt_date])

    rpt_rows = [['Domain', 'Count', 'Percentage']]
    for db_row in cursor:
        row = list(db_row)
        row[1] = f'{row[1]}'
        rpt_rows.append(row)

    return rpt_rows

# End: rpt_top_domains()


def rpt_top_queries(ddi: clintosaurous.ddi.connect) -> list:

    """
    Top queries for all client query summary report.
    """

    # Type hints.
    if not isinstance(ddi, clintosaurous.ddi.connect):
        raise TypeError(
            f'db expected `clintosaurous.ddi.connect`, received {type(ddi)}')

    sql = """
        select dns_name, count, concat(percentage, '%%')
        from reports.dns_top_name_queries
        where datestamp = %s
        order by count desc
    """
    cursor = ddi.db.cursor()
    cursor.execute(sql, [rpt_date])

    rpt_rows = [['Request', 'Count', 'Percentage']]
    for db_row in cursor:
        row = list(db_row)
        row[1] = f'{row[1]:,}'
        rpt_rows.append(row)

    return rpt_rows

# End: rpt_top_queries()


if __name__ == '__main__':
    cgi = clintosaurous.cgi.cgi(
        title='DNS Reports',
        version=VERSION,
        last_update=LAST_UPDATE,
        copyright=2022
    )

    print(cgi.start_page())
    print(cgi.hr())

    rpt_date = cgi.form_values.getvalue("date")
    if rpt_date is None:
        rpt_date = datestamp(time.time() - 86400)
    start_time = f'{rpt_date} 00:00:00'
    end_time = f'{rpt_date} 23:59:59'

    ddi = clintosaurous.ddi.connect(logging=False)
    ddi_dev = clintosaurous.ddi.connect(
        db_name='clintosaurous_dev',
        logging=False
    )
    client_hosts = None

    print(cgi.form(**rpt_form_options(ddi)))
    if cgi.form_values.getvalue("client_block") is not None:
        display_block_client(ddi, ddi_dev)
        ddi_dev.close()
    elif cgi.form_values.getvalue("client_requests") is not None:
        ddi_dev = clintosaurous.ddi.connect(
            db_name='clintosaurous_dev',
            logging=False
        )
        display_client_requests(ddi, ddi_dev)
        ddi_dev.close()
    else:
        display_report(ddi)

    ddi.close()

    print(cgi.end_page())
