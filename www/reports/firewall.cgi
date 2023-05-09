#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
Display report data from reports table.
"""


import clintosaurous.cgi
import clintosaurous.credentials as credentials
from clintosaurous.datetime import datestamp
import clintosaurous.db
import time


VERSION = '2.6.2'
LAST_UPDATE = '2023-01-29'


def display_host(db: clintosaurous.db.connect, rule_type: str) -> None:

    """
    Display firewall messages fore specific host.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')
    if not isinstance(rule_type, str):
        raise TypeError(
            f'`rule_type` expected `str`, received {type(rule_type)}')

    print(cgi.hr())

    ip = cgi.form_values.getvalue("src_ip")
    rule_type = cgi.form_values.getvalue("rule_type")
    disp_name = cgi.form_values.getvalue("disp_name")
    total_msgs = cgi.form_values.getvalue("total_msgs")

    if total_msgs is None:
        sql = """
            select count(timestamp)
            from firewall_messages
            where
                timestamp between %s and %s
                and src_ip = %s
                and rule_type = %s
            order by timestamp
        """
        cursor = db.cursor()
        cursor.execute(sql, [start_time, end_time, ip, rule_type])
        total_msgs = cursor.fetchone()[0]

    else:
        total_msgs = int(total_msgs)

    page, page_cnt, per_page, start_record = parse_page(total_msgs)

    sql = """
        select
            timestamp, host, interface, rule,
            case
                when dst_dns_name is not null
                    then concat(dst_ip, ' (', dst_dns_name, ')')
                else dst_ip
            end as dst_host,
            protocol, src_port, dst_port,
            country_code, region_name, city_name
        from firewall_messages
        where
            timestamp between %s and %s
            and src_ip = %s
            and rule_type = %s
        order by timestamp desc
        limit %s, %s
    """
    cursor = db.cursor()
    cursor.execute(sql, [
        start_time, end_time, ip, rule_type, start_record, per_page])

    rpt_rows = [[
        'Timestamp', 'Host', 'Interface', 'Rule',
        'Destination',
        'Protocol', 'Src Port', 'Dst Port',
        'Country', 'Region', 'City'
    ]]
    for db_row in cursor:
        row = list(db_row)
        for i in range(len(row)):
            if row[i] is None:
                row[i] = ''
        rpt_rows.append(row)
    cursor.close()

    form_txt = """
        <p><form action="firewall.cgi" name="page_select" method="put" >
        <input type="hidden" name="date" value="{}" />
        <input type="hidden" name="rule_type" value="{}" />
        <input type="hidden" name="disp_name" value="{}" />
        <input type="hidden" name="host_filter" value="View" />
        <input type="hidden" name="src_ip" value="{}" />
        <input type="hidden" name="page" value="{}" />
        <input type="hidden" name="total_msgs" value="{}" />
    """.format(rpt_date, rule_type, disp_name, ip, page, total_msgs)

    form_txt += page_buttons(page, page_cnt, total_msgs)

    title = (
        f'All {rule_type.capitalize()} Messages for {disp_name} ' +
        f'From {rpt_date}'
    )
    print(cgi.text_box(cgi.table(rpt_rows), title))
    print(form_txt)

# End: display_host()


def display_pair(db: clintosaurous.db.connect, rule_type: str) -> None:

    """
    Display firewall message report for specific pair of hosts.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')
    if not isinstance(rule_type, str):
        raise TypeError(
            f'`rule_type` expected `str`, received {type(rule_type)}')

    print(cgi.hr())

    ip1 = cgi.form_values.getvalue("ip1")
    ip2 = cgi.form_values.getvalue("ip2")
    rule_type = cgi.form_values.getvalue("rule_type")

    disp_name1 = cgi.form_values.getvalue("disp_name1")
    disp_name2 = cgi.form_values.getvalue("disp_name2")

    total_msgs = cgi.form_values.getvalue("total_msgs")

    if total_msgs is None:
        sql = """
            select count(timestamp)
            from firewall_messages
            where
                timestamp between %s and %s
                and src_ip = %s
                and dst_ip = %s
                and rule_type = %s
        """
        cursor = db.cursor()
        cursor.execute(sql, [start_time, end_time, ip1, ip2, rule_type])
        total_msgs = cursor.fetchone()[0]

    else:
        total_msgs = int(total_msgs)

    page, page_cnt, per_page, start_record = parse_page(total_msgs)

    sql = """
        select
            timestamp, host, interface, rule,
            protocol, src_port, dst_port,
            country_code, region_name, city_name
        from firewall_messages
        where
            timestamp between %s and %s
            and src_ip = %s
            and dst_ip = %s
            and rule_type = %s
        order by timestamp
        limit %s, %s
    """
    cursor = db.cursor()
    cursor.execute(sql, [
        start_time, end_time, ip1, ip2, rule_type, start_record, per_page])

    rpt_rows = [[
        'Timestamp', 'Host', 'Interface', 'Rule',
        'Protocol', 'Src Port', 'Dst Port',
        'Country', 'Region', 'City'
    ]]
    for db_row in cursor:
        row = list(db_row)
        for i in range(len(row)):
            if row[i] is None:
                row[i] = ''
        rpt_rows.append(row)
    cursor.close()

    form_txt = """
        <p><form action="" name="page_select" method="put" >

        <input type="hidden" name="date" value="{}" />
        <input type="hidden" name="rule_type" value="{}" />
        <input type="hidden" name="pair_filter" value="View" />
        <input type="hidden" name="disp_name1" value="{}" />
        <input type="hidden" name="disp_name2" value="{}" />
        <input type="hidden" name="ip1" value="{}" />
        <input type="hidden" name="ip2" value="{}" />
        <input type="hidden" name="page" value="{}" />
        <input type="hidden" name="total_msgs" value="{}" />
    """.format(
        rpt_date, rule_type,
        disp_name1, disp_name2,
        ip1, ip2,
        page, total_msgs
    )

    form_txt += page_buttons(page, page_cnt, total_msgs)

    title = (
        f'All {rule_type.capitalize()} Messages from {disp_name1} to ' +
        f'{disp_name2} for {rpt_date}'
    )
    print(cgi.text_box(cgi.table(rpt_rows) + form_txt, title))

# End: display_pair()


def display_report(db: clintosaurous.db.connect) -> None:

    """
    Display summary report of firewall messages.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    print(cgi.hr())

    # Message counts.
    title = f'All Messages Report for {rpt_date}'
    sql = """
        select
            firewalls.host as firewall,
            block_cnt.total as block_cnt,
            pass_cnt.total as pass_cnt,
            block_cnt.total + pass_cnt.total as total
        from (
            select distinct fw.host
            from firewall_messages as fw
            where fw.timestamp between %s and %s
        ) as firewalls

        inner join (
            select blk.host, count(blk.host) as total
            from firewall_messages as blk
            where
                blk.timestamp between %s and %s
                and blk.rule_type = 'block'
            group by blk.host
        ) as block_cnt
            on block_cnt.host = firewalls.host

        inner join (
            select pss.host, count(pss.host) as total
            from firewall_messages as pss
            where
                pss.timestamp between %s and %s
                and pss.rule_type = 'pass'
            group by pss.host
        ) as pass_cnt
            on pass_cnt.host = firewalls.host

        order by firewalls.host
    """
    sql_values = [
        start_time, end_time,
        start_time, end_time,
        start_time, end_time
    ]
    cursor = db.cursor()
    cursor.execute(sql, sql_values)

    rpt_rows = [['Firewall', 'Block', 'Pass', 'Total']]
    block_total = 0
    pass_total = 0
    for db_row in cursor:
        row = list(db_row)
        block_total += row[1]
        pass_total += row[2]
        for i in range(1, 4):
            row[i] = f'{row[i]:,}'
        rpt_rows.append(list(row))
    cursor.close()

    total = f'{block_total + pass_total:,}'
    block_total = f'{block_total:,}'
    pass_total = f'{pass_total:,}'
    rpt_rows.append(['Total', block_total, pass_total, total])

    print(cgi.text_box(cgi.table(rpt_rows), title))

    reports = [
        [f'Malware Rule Hits for {rpt_date}', rpt_malware_summary],
        [f'VPN Rule Messages for {rpt_date}', rpt_vpn_msgs],
        [f'VPN Connections for {rpt_date}', rpt_vpn_connects],
        [f'Protocol Summary for {rpt_date}', rpt_proto_summary],
        [f'DoH Counts {rpt_date}', rpt_doh_counts],
        [f'Host Counts for {rpt_date}', rpt_host_counts],
        [f'Host Pairs for {rpt_date}', rpt_host_pairs]
    ]
    for title, function in reports:
        print(cgi.hr())
        rpt_rows = function(db)
        if rpt_rows:
            print(cgi.text_box(cgi.table(rpt_rows), title))
        else:
            print(cgi.text_box('No report records returned', title))

# End: display_report()


def page_buttons(page: int, page_cnt: int, total_msgs: int) -> str:

    """
    Generate HTML for paging buttons.
    """

    # Type hints.
    if not isinstance(page, int):
        raise TypeError(f'page expected `int`, received {type(page)}')
    if not isinstance(page_cnt, int):
        raise TypeError(f'page_cnt expected `int`, received {type(page_cnt)}')
    if not isinstance(total_msgs, int):
        raise TypeError(
            f'total_msgs expected `int`, received {type(total_msgs)}')

    form_txt = ''

    if page > 1:
        form_txt += '<input type="submit" name="prev_page" value="Prev" />\n'

    if page_cnt > 1:
        form_txt += """
            Page <input type="text" name="user_page"
                value="{}" style="width: 10px" /> of {} ({} total messages)
        """.format(page, page_cnt, total_msgs)
    else:
        form_txt += 'Page 1 of 1'

    if page < page_cnt:
        form_txt += '<input type="submit" name="next_page" value="Next" />\n'

    form_txt += '\n</form></p>\n'

    return form_txt

# End: page_buttons()


def parse_page(total_msgs: int) -> tuple[int, int, int, int]:

    """
    Parse paging data from submitted HTML form.
    """

    # Type hints.
    if not isinstance(total_msgs, int):
        raise TypeError(
            f'total_msgs expected `int`, received {type(total_msgs)}')

    per_page = 250

    page_cnt = int(total_msgs / per_page)
    if total_msgs % per_page:
        page_cnt += 1

    page = cgi.form_values.getvalue("page")
    if page is None:
        page = 1
    else:
        page = int(page)

    user_page = cgi.form_values.getvalue("user_page")
    if user_page is not None:
        user_page = int(user_page)
    else:
        user_page = page

    if user_page != page and user_page <= page_cnt:
        page = int(user_page)

    else:
        if cgi.form_values.getvalue("prev_page") is not None:
            page -= 1
            if page < 1:
                page = 1
        if cgi.form_values.getvalue("next_page") is not None:
            page += 1
            if page > page_cnt:
                page = page_cnt

    start_record = per_page * (page - 1)

    return page, page_cnt, per_page, start_record

# End: parse_page()


def rpt_doh_counts(db: clintosaurous.db.connect) -> list[list]:

    """
    Generate report rows for DoH block messags.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select
            case
                when src_dns_name is not null
                    then concat(src_ip, ' (', src_dns_name, ')')
                else src_ip
            end as src_host,
            count(src_ip)
        from firewall_doh_counts
        where timestamp between %s and %s
        group by src_host
        order by src_host
    """
    cursor = db.cursor()
    cursor.execute(sql, [start_time, end_time])

    rpt_rows = [['Source', 'Count']]

    total = 0
    for db_row in cursor:
        row = list(db_row)
        total += row[1]
        rpt_rows.append(row)
    cursor.close()

    rpt_rows.append(['Total:', total])

    return rpt_rows

# End: rpt_doh_counts()


def rpt_host_counts(db: clintosaurous.db.connect) -> list[list]:

    """
    Generate firewall messages per host summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select
            src_ip,
            src_dns_name,
            count,
            concat(percentage, '%%') as total_percent

        from firewall_src_ip_counts

        where
            datestamp = %s
            and rule_type = %s

        group by
            src_ip,
            src_dns_name

        order by
            count desc
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date, rule_type])

    rpt_rows = [['Source', 'Count', 'Percentage', '']]
    count = 0
    for db_row in cursor:
        row = list(db_row)
        count += 1
        disp_name = row[0]
        if row[1] and row[0] != row[1]:
            disp_name += f' ({row[1]})'

        form_html = cgi.form(
            method='put',
            hidden=[
                {"name": "date", "value": rpt_date, "override": True},
                {"name": "rule_type", "value": rule_type, "override": True},
                {"name": "disp_name", "value": disp_name, "override": True},
                {"name": "src_ip", "value": row[0], "override": True},
                {"name": "page", "value": 1, "override": True}
            ],
            buttons=[{"name": "host_filter", "value": "View"}]
        )

        rpt_rows.append([disp_name, f'{row[2]:,}', row[3], form_html])

    cursor.close()

    return rpt_rows

# End: rpt_host_counts()


def rpt_host_pairs(db: clintosaurous.db.connect) -> list[list]:

    """
    Generate per source and destination summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select
            src_ip, src_dns_name, dst_ip, dst_dns_name,
            count, concat(percentage, '%%')
        from firewall_host_pairs
        where
            datestamp = %s
            and rule_type = %s
        order by count desc
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date, rule_type])

    rpt_rows = [['Source', 'Destination', 'Count', 'Percentage', '']]
    count = 0
    for db_row in cursor:
        row = list(db_row)
        count += 1
        src_name = row[0]
        if row[1] is not None and row[0] != row[1]:
            src_name += f' ({row[1]})'
        dst_name = row[2]
        if row[3] is not None and row[2] != row[3]:
            dst_name += f' ({row[3]})'

        form_html = cgi.form(
            method="put",
            hidden=[
                {"name": "date", "value": rpt_date, "override": True},
                {"name": "ip1", "value": row[0], "override": True},
                {"name": "ip2", "value": row[2], "override": True},
                {"name": "disp_name1", "value": src_name, "override": True},
                {"name": "disp_name2", "value": dst_name, "override": True},
                {"name": "rule_type", "value": rule_type, "override": True}
            ],
            buttons=[{"name": "pair_filter", "value": "View"}]
        )

        rpt_rows.append([
            src_name, dst_name, f'{row[4]:,}', row[5], form_html])

    cursor.close()

    return rpt_rows

# End: rpt_host_pairs()


def rpt_form_options(db: clintosaurous.db.connect) -> dict:

    """
    Form options for main page form.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select distinct datestamp
        from firewall_host_pairs
        order by datestamp desc
    """
    cursor = db.cursor()
    cursor.execute(sql)
    dates = []
    for row in cursor:
        dates.append(str(row[0]))
    cursor.close()

    options = {
        "method": 'put',
        "fields": [
            {
                "type": 'dropdown',
                "name": 'date',
                "title": 'Date',
                "default": dates[0],
                "values": dates
            },
            {
                "type": 'dropdown',
                "name": 'rule_type',
                "title": 'Rule Type',
                "default": 'block',
                "values": ["block", "pass"],
                "labels": {"block": "Blocked", "pass": "Passed"}
            }
        ],
        "buttons": [{"name": 'submit_view', "value": 'View'}]
    }

    return options

# End: rpt_form_options()


def rpt_malware_summary(db: clintosaurous.db.connect) -> list[list]:

    """
    Generate per host malware block rules summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select src_ip, src_dns_name, rule, count(src_ip)
        from firewall_messages
        where
            timestamp between %s and %s
            and lower(rule) like '%%malware%%'
        group by src_ip, src_dns_name, rule
    """
    cursor = db.cursor()
    cursor.execute(sql, [start_time, end_time])

    rpt_rows = [['Source', 'Rule', 'Count']]
    total = 0
    for db_row in cursor:
        row = list(db_row)
        total += row[3]
        if row[1] is not None:
            disp_name = f'{row[1]} ({row[0]})'
        else:
            disp_name = row[0]
        rpt_rows.append([disp_name, row[2], f'{row[3]:,}'])

    rpt_rows.append(['Total:', "", f'{total:,}'])

    return rpt_rows

# End: rpt_malware_summary()


def rpt_proto_summary(db: clintosaurous.db.connect) -> list[list]:

    """
    Generate protocol breakout summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select protocol, count, concat(percentage, '%%')
        from firewall_protocol_summary
        where
            datestamp = %s
            and rule_type = %s
        order by count desc
    """
    cursor = db.cursor()
    row_cnt = cursor.execute(sql, [rpt_date, rule_type])

    rpt_rows = [['Protocol', 'Count', 'Percentage']]
    total = 0
    for db_row in cursor:
        row = list(db_row)
        total += row[1]
        row[1] = f'{row[1]:,}'
        rpt_rows.append(row)

    rpt_rows.append(['Total:', f'{total:,}', '100.00%'])

    return rpt_rows

# End: rpt_proto_summary()


def rpt_vpn_connects(db: clintosaurous.db.connect) -> list[list]:

    """
    Generate VPN connections summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select
            timestamp,
            host,
            case
                when src_dns_name is not null
                    then concat(src_ip, ' (', src_dns_name, ')')
                else src_ip
            end as src_host,
            country_code,
            region_name,
            city_name

        from firewall_messages

        where
            timestamp between %s and %s
            and dst_ip = '192.168.1.5'
            and (
                dst_port = '8194'
                or dst_port like '8194/%%'
            )

        order by timestamp
    """
    cursor = db.cursor()
    cursor.execute(sql, [start_time, end_time])

    rpt_rows = []
    for row in cursor:
        rpt_rows.append(list(row))
    cursor.close()

    if len(rpt_rows):
        rpt_rows.insert(0, [
            'Timestamp', 'Host', 'Source', 'Country', 'Region', 'City'])
        return rpt_rows

    return None

# End: rpt_vpn_connects()


def rpt_vpn_msgs(db: clintosaurous.db.connect) -> list[list]:

    """
    Generate VPN firewall message summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select
            timestamp,
            host,
            case
                when src_dns_name is not null
                    then concat(src_ip, ' (', src_dns_name, ')')
                else src_ip
            end as src_host,
            message_type,
            user,
            message,
            country_code,
            region_name,
            city_name,
            time_zone
        from firewall_vpn_messages
        where timestamp between %s and %s
        order by timestamp
    """
    cursor = db.cursor()
    cursor.execute(sql, [start_time, end_time])

    rpt_rows = []
    for db_row in cursor:
        row = list(db_row)
        row[4] = row[4].capitalize()
        rpt_rows.append(row)
    cursor.close()

    if len(rpt_rows):
        rpt_rows.insert(0, [
            'Timestamp', 'Host', 'Source', 'Message Type', 'User', 'Message'])
        return rpt_rows

    return None

# End: rpt_vpn_msgs()


if __name__ == '__main__':
    cgi = clintosaurous.cgi.cgi(
        title='Firewall Reports',
        version=VERSION,
        last_update=LAST_UPDATE,
        copyright=2023
    )

    print(cgi.start_page())
    print(cgi.hr())

    rpt_date = cgi.form_values.getvalue("date")
    if rpt_date is None:
        rpt_date = datestamp(time.time() - 86400)
    start_time = f'{rpt_date} 00:00:00'
    end_time = f'{rpt_date} 23:59:59'

    if cgi.form_values.getvalue("rule_type") == 'Passed':
        rule_type= 'pass'
    else:
        rule_type = 'block'

    user, passwd = credentials.data().get('mysql-report_ro')
    db = clintosaurous.db.connect(
        host='mysql1.clintosaurous.com',
        user=user,
        passwd=passwd,
        database='reports',
        logging=False
    )

    form_opts = rpt_form_options(db)
    print(cgi.form(**form_opts))

    if cgi.form_values.getvalue("host_filter") is not None:
        display_host(db, rule_type)
    elif cgi.form_values.getvalue("pair_filter") is not None:
        display_pair(db, rule_type)
    else:
        display_report(db)

    db.close()

    print(cgi.end_page())
