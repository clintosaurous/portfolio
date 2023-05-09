#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
Displays a summary of the tables in the reports database.
"""


import clintosaurous.cgi
import clintosaurous.credentials as credentials
from clintosaurous.datetime import datestamp
import clintosaurous.db
import clintosaurous.file
import time


VERSION = '2.2.0'
LAST_UPDATE = '2022-10-28'


def disp_rpt_dns(db: clintosaurous.db.connect) -> None:

    """
    Display DNS queries summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    title = 'DNS Query Report'
    summary = '<p>DNS query count summary report.</p>\n'

    sql = """
        select
            'Total Queries' as row_type,
            q1.count,
            q1.datestamp,
            q2.count as prev_count,
            q2.datestamp as prev_datestamp,
            q1.count - q2.count as difference

        from (
            select
                sum(q1a.count) as 'count',
                q1a.datestamp
            from dns_queries_per_server as q1a
            where q1a.datestamp = %s
        ) as q1

        inner join (
            select
                sum(q2a.count) as 'count',
                q2a.datestamp
            from dns_queries_per_server as q2a
            where
                q2a.datestamp = (
                    select max(q2b.datestamp)
                    from dns_ad_malware_queries as q2b
                    where q2b.datestamp < %s
                )
            group by q2a.datestamp
        ) as q2
            on q2.datestamp != q1.datestamp

        union

        select
            'Ad/Malware Queries' as row_type,
            m1.count,
            m1.datestamp,
            m2.count as prev_count,
            m2.datestamp as prev_datestamp,
            m1.count - m2.count as difference

        from (
            select
                sum(m1a.count) as 'count',
                m1a.datestamp
            from dns_ad_malware_queries as m1a
            where m1a.datestamp = %s
        ) as m1

        inner join (
            select
                sum(m2a.count) as 'count',
                m2a.datestamp
            from dns_ad_malware_queries as m2a
            where
                m2a.datestamp = (
                    select max(m2b.datestamp)
                    from dns_ad_malware_queries as m2b
                    where m2b.datestamp < %s
                )
            group by m2a.datestamp
        ) as m2
            on m2.datestamp != m1.datestamp
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date, rpt_date, rpt_date, rpt_date])

    rows = [['', 'Count', 'Date', 'Previous', 'Date', 'Diff.']]

    for db_row in cursor:
        row = list(db_row)
        row[1] = f'{int(row[1]):,}'
        row[3] = f'{int(row[3]):,}'
        row[5] = f'{int(row[5]):,}'
        rows.append(row)

    cursor.close()

    html = summary + cgi.table(rows)

    print(cgi.text_box(html, title))

# End: disp_rpt_dns


def disp_rpt_firewall(db: clintosaurous.db.connect) -> None:

    """
    Display firewall messages summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    title = 'Firewall Messages Report'
    summary = '<p>Firewall messages count summary report.</p>\n'

    sql = """
        select
            'Total' as rule_type,
            f1.count,
            f1.datestamp,
            f2.count as prev_count,
            f2.datestamp as prev_datestamp,
            f1.count - f2.count as difference

        from (
            select
                sum(f1a.count) as 'count',
                f1a.datestamp
            from firewall_protocol_summary as f1a
            where f1a.datestamp = %s
        ) as f1

        inner join (
            select
                sum(f2a.count) as 'count',
                f2a.datestamp
            from firewall_protocol_summary as f2a
            where
                f2a.datestamp = (
                    select max(f2b.datestamp)
                    from firewall_protocol_summary as f2b
                    where f2b.datestamp < %s
                )
            group by f2a.datestamp
        ) as f2
            on f2.datestamp != f1.datestamp

        union

        select
            r1.rule_type,
            r1.count,
            r1.datestamp,
            r2.count as prev_count,
            r2.datestamp as prev_datestamp,
            r1.count - r2.count as difference

        from (
            select
                r1a.rule_type,
                sum(r1a.count) as 'count',
                r1a.datestamp
            from firewall_protocol_summary as r1a
            where r1a.datestamp = %s
            group by r1a.rule_type, r1a.datestamp
            order by r1a.rule_type
        ) as r1

        inner join (
            select
                r2a.rule_type,
                sum(r2a.count) as 'count',
                r2a.datestamp
            from firewall_protocol_summary as r2a
            where
                r2a.datestamp = (
                    select max(r2b.datestamp)
                    from firewall_protocol_summary as r2b
                    where r2b.datestamp < %s
                )
            group by r2a.rule_type, r2a.datestamp
            order by r2a.rule_type
        ) as r2
            on r2.rule_type = r1.rule_type
            and r2.datestamp != r1.datestamp
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date, rpt_date, rpt_date, rpt_date])

    rows = [['Rule Type', 'Count', 'Date', 'Previous', 'Date', 'Diff.']]

    for db_row in cursor:
        row = list(db_row)
        row[1] = f'{int(row[1]):,}'
        row[3] = f'{int(row[3]):,}'
        row[5] = f'{int(row[5]):,}'
        rows.append(row)

    cursor.close()

    html = summary + cgi.table(rows)

    print(cgi.text_box(html, title))

# End: disp_rpt_firewall()


def disp_rpt_syslog(db: clintosaurous.db.connect) -> None:

    """
    Display syslog summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    title = 'syslog Messages Report'
    summary = '<p>Total syslog messages by host.</p>\n'

    sql = """
        select
            'Total Messages' as host,
            t1.count,
            t1.datestamp,
            t2.count,
            t2.datestamp,
            t1.count - t2.count as difference

        from (
            select sum(t1a.count) as count, t1a.datestamp
            from syslog_host_total_messages as t1a
            where t1a.datestamp = %s
        ) as t1

        inner join (
            select sum(t2a.count) as count, t2a.datestamp
            from syslog_host_total_messages as t2a
            where t2a.datestamp = (
                select max(t2b.datestamp)
                from syslog_host_total_messages as t2b
                where t2b.datestamp < %s
            )
            group by t2a.datestamp
        ) as t2
            on t2.datestamp < t1.datestamp

        union

        select * from (
            select
                m1.host,
                m1.count,
                m1.datestamp,
                case
                    when p1.count is not null then p1.count
                    else 0
                end as prev_count,
                case
                    when p1.datestamp is not null then p1.datestamp
                    else CURRENT_DATE()
                end as prev_datestamp,
                case
                    when p1.count is not null then m1.count - p1.count
                    else m1.count
                end as difference

            from syslog_host_total_messages as m1

            left join syslog_host_total_messages as p1
                on p1.host = m1.host
                and p1.datestamp = (
                    select max(p2.datestamp)
                    from syslog_host_total_messages as p2
                    where p2.datestamp < %s
                )

            where m1.datestamp = %s

            order by m1.host
        ) as by_hosts
    """
    cursor = db.cursor()
    cursor.execute(sql, (rpt_date, rpt_date, rpt_date, rpt_date))

    rows = [['Host', 'Count', 'Date', 'Previous', 'Date', 'Diff.']]

    for db_row in cursor:
        row = list(db_row)
        row[1] = f'{int(row[1]):,}'
        row[3] = f'{int(row[3]):,}'
        row[5] = f'{int(row[5]):,}'
        rows.append(row)

    cursor.close()

    html = summary + cgi.table(rows)

    print(cgi.text_box(title, html))

# End: disp_rpt_syslog()


def disp_rpt_vpn(db: clintosaurous.db.connect) -> None:

    """
    Display VPN connections summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    title = 'VPN Connections Report'
    summary = '<p>Total VPN connection messages.</p>\n'

    sql = """
        select 'Total' as user, count(t1.msg_id)
        from firewall_vpn_messages as t1
        where t1.timestamp between %s and %s

        union

        select * from (
            select user, count(c1a.user) as 'count'
            from firewall_vpn_messages as c1a
            where c1a.timestamp between %s and %s
            group by user
            order by c1a.user
        ) as c1
    """
    cursor = db.cursor()
    cursor.execute(sql, [start_time, end_time, start_time, end_time])

    rows = [['Username', 'Count']]

    for db_row in cursor:
        row = list(db_row)
        row[1] = f'{int(row[1]):,}'
        rows.append(row)

    cursor.close()

    html = summary + cgi.table(rows)

    print(cgi.text_box(html, title))

# End: disp_rpt_vpn()


def rpt_form_options(db: clintosaurous.db.connect) -> tuple[dict,str]:

    """
    Options used to build the date form.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select distinct datestamp
        from syslog_host_total_messages
        order by datestamp desc
    """
    cursor = db.cursor()
    cursor.execute(sql)
    dates = []

    for row in cursor:
        dates.append(str(row[0]))

    cursor.close()

    options = {
        "title": 'Report Date Selection',
        "method": 'put',
        "fields": [
            {
                "type": 'dropdown',
                "name": 'rpt_date',
                "title": 'Date',
                "default": dates[0],
                "values": dates
            }
        ],
        "buttons": [{"name": 'submit_view', "value": 'View'}]
    }

    date = cgi.form_values.getvalue("rpt_date")
    if date is None:
        date = dates[0]

    return options, date

# End: rpt_form_options()


if __name__ == '__main__':
    cgi = clintosaurous.cgi.cgi(
        title='Daily Reports Summary',
        version=VERSION,
        last_update=LAST_UPDATE,
        copyright=2022
    )

    print(cgi.start_page())

    user, passwd = credentials.data().get('mysql-report_ro')
    db = clintosaurous.db.connect(
        host='mysql1.clintosaurous.com',
        user=user,
        passwd=passwd,
        database='reports',
        logging=False
    )

    rpt_date = cgi.form_values.getvalue("rpt_date")
    if rpt_date is None:
        rpt_date = datestamp(time.time() - 86400)
    start_time = f'{rpt_date} 00:00:00'
    end_time = f'{rpt_date} 23:59:59'

    form_options, rpt_date = rpt_form_options(db)
    print(cgi.form(**form_options))
    print(cgi.hr())
    disp_rpt_dns(db)
    print(cgi.hr())
    disp_rpt_firewall(db)
    print(cgi.hr())
    disp_rpt_vpn(db)
    print(cgi.hr())
    disp_rpt_syslog(db)

    db.close()

    print(cgi.end_page())
