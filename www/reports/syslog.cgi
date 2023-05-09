#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
Display syslog report data from reports table.
"""


import clintosaurous.cgi
import clintosaurous.credentials as credentials
from clintosaurous.datetime import datestamp
import clintosaurous.db
import time


VERSION = '2.3.1'
LAST_UPDATE = '2022-10-28'


def display_report(db: clintosaurous.db.connect) -> None:

    """
    Display syslog message summary report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select t.total, l.ldate, l.total

        from (
            select t1.datestamp, sum(t1.count) as total
            from syslog_host_total_messages as t1
            where t1.datestamp = %s
            group by t1.datestamp
        ) as t

        left join (
            select
                %s as cdate,
                l1.datestamp as 'ldate',
                sum(l1.count) as total
            from syslog_host_total_messages as l1
            where
                l1.datestamp = (
                    select max(l2.datestamp)
                    from syslog_host_total_messages as l2
                    where l2.datestamp < %s
                )
            group by l1.datestamp
        ) as l
            on l.cdate = t.datestamp
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date, rpt_date, rpt_date])
    row = cursor.fetchone()
    cur_total, prev_date, prev_total = row
    if prev_date is None:
        prev_date = 'None'
    if prev_total is None:
        prev_total = 0
    cursor.close()

    delta = f'{int(cur_total - prev_total):,}'
    cur_total = f'{int(cur_total):,}'
    prev_total = f'{int(prev_total):,}'

    rows = [
        [rpt_date, prev_date, 'Delta'],
        [cur_total, prev_total, delta]
    ]
    print(cgi.hr())
    print(cgi.text_box(cgi.table(rows), 'Total Messages'))

    title = 'Log Levels'
    rows = rpt_log_level(db)
    print(cgi.hr())
    print(cgi.text_box(cgi.table(rows), title))

    title = 'Message Priority Summary'
    rows = rpt_priority_summary(db)
    print(cgi.hr())
    print(cgi.text_box(cgi.table(rows), title))

    title = 'High Priority Messages by Host'
    rows = rpt_priority_hosts(db)
    print(cgi.hr())
    print(cgi.text_box(cgi.table(rows), title))

    title = 'Total Messages by Host'
    rows = rpt_host_counts(db)
    print(cgi.hr())
    print(cgi.text_box(cgi.table(rows), title))

    title = 'Top Process Messages'
    rows = rpt_top_process_counts(db)
    print(cgi.hr())
    print(cgi.text_box(cgi.table(rows), title))

    title = 'Top Process Messages by Host'
    rows = rpt_top_host_processes(db)
    print(cgi.hr())
    print(cgi.text_box(cgi.table(rows), title))

# End: display_report()


def display_trending(db: clintosaurous.db.connect) -> bool:

    """
    Display summary of total number of syslog messages by host.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    if cgi.form_values.getvalue('submit_trend') is None:
        return False

    sql = """
        select datestamp, host, sum(count) as total
        from syslog_host_total_messages
        where datediff(current_date(), datestamp) <= 30
        group by datestamp, host
    """
    cursor = db.cursor()
    cursor.execute(sql)

    host_totals = {}
    totals = {}
    for db_row in cursor:
        row = list(db_row)
        row[2] = int(row[2])

        try:
            totals[row[0]] += row[2]
        except KeyError:
            totals[row[0]] = row[2]

        try:
            host = host_totals[row[1]]
        except KeyError:
            host_totals[row[1]] = {}
            host = host_totals[row[1]]

        try:
            host[row[0]] += row[2]
        except KeyError:
            host[row[0]] = row[2]

    cursor.close()

    daily_rows = []
    prev_cnt = 0
    for date in sorted(totals.keys()):
        cnt = totals[date]
        if prev_cnt:
            delta = cnt - prev_cnt
        else:
            delta = 0

        daily_rows.append([date, f'{cnt:,}', f'{delta:,}'])
        prev_cnt = cnt

    daily_rows.reverse()

    print(cgi.hr())
    headings = ['Date', 'Count', 'Delta']
    print(cgi.text_box(cgi.table_split(headings, daily_rows), 'Daily Totals'))

    for hostname in sorted(host_totals.keys()):
        totals = host_totals[hostname]
        daily_rows = []
        prev_cnt = 0
        for date in sorted(totals.keys()):
            cnt = totals[date]
            if prev_cnt:
                delta = cnt - prev_cnt
            else:
                delta = 0

            daily_rows.append([
                date, f'{cnt:,}', f'{delta:,}'
            ])
            prev_cnt = cnt

        daily_rows.reverse()

        print(cgi.hr())
        print(cgi.text_box(
            cgi.table_split(headings, daily_rows),
            f'{hostname} Daily Totals'
        ))

    return True

# End: display_trending()


def form_options(db: clintosaurous.db.connect) -> dict:

    """
    Date selection HTML form options.
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
    for big_d in cursor:
        dates.append(str(big_d[0]))
    cursor.close()

    options = {
        "title": 'Report Selection',
        "method": 'put',
        "fields": [
            {
                "type": 'dropdown',
                "name": 'date',
                "title": 'Date',
                "default": dates[0],
                "values": dates
            }
        ],
        "buttons": [
            {"name": 'submit_view', "value": 'View'},
            {"name": 'submit_trend', "value": 'Trending'}
        ]
    }

    return options

# End: form_options()


def page_buttons(page, page_cnt, total_msgs) -> str:

    """
    Generate paging buttons HTML.
    """

    # Type hints.
    if not isinstance(page, int):
        raise TypeError(f'page expected `int`, received {type(page)}')
    if not isinstance(page_cnt, int):
        raise TypeError(f'page_cnt expected `int`, received {type(page_cnt)}')
    if not isinstance(total_msgs, int):
        raise TypeError(
            f'total_msgs expected `int`, received {type(total_msgs)}')

    form_txt = f'Page {page} of {page_cnt} (Total: {total_msgs:,})'

    if page > 1:
        form_txt += '<input type="submit" name="prev_page" value="Prev" />\n'

    if page < page_cnt:
        form_txt += '<input type="submit" name="next_page" value="Next" />\n'

    form_txt += '\n</form></p>\n'

    return form_txt

# End: page_buttons()


def parse_page(total_msgs: int) -> tuple[int, int, int]:

    """
    Determing paging information.
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
        if cgi.form_values.getvalue("prev_page") is not None:
            page -= 1
            if page < 1:
                page = 1
        if cgi.form_values.getvalue("next_page") is not None:
            page += 1
            if page > page_cnt:
                page = page_cnt

    if page == 1:
        start_record = 0
    else:
        start_record = per_page * (page - 1)

    return page, page_cnt, per_page, start_record

# End: parse_page()


def rpt_host_counts(db: clintosaurous.db.connect) -> list:

    """
    Generate host total log messages report data.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select host, count, concat(percentage, '%%')
        from syslog_host_total_messages
        where datestamp = %s
        order by host
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date])

    count = 0
    rpt_rows = [['Host', 'Count', '% of All']]
    for db_row in cursor:
        row = list(db_row)
        total_msgs = row[1]
        row[1] = f'{row[1]:,}'
        count += 1
        form_txt = f"""
            <form method="put"
                enctype="multipart/form-data" name="per_host{count}">
            <input type="hidden" name="date" value="{rpt_date}" />
            <input type="hidden" name="host" value="{row[0]}" />
            <input type="hidden" name="page" value="1" />
            <input type="hidden" name="total_msgs" value="{total_msgs}" />
            <input type="submit" name="per_host" value="View" />
        """.strip()
        form_txt += '</form>\n'
        row.append(form_txt)
        rpt_rows.append(row)

    cursor.close()

    return rpt_rows

# End: rpt_host_counts()


def rpt_log_level(db: clintosaurous.db.connect) -> list:

    """
    Generates total count of log messages per log level.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = 'select level, name, descr from syslog_levels order by level'
    cursor = db.cursor()
    cursor.execute(sql)
    row = cursor.fetchall()
    cursor.close()
    return_rows = [
        [
            'Level', 'Name', 'Description',
            'Level', 'Name', 'Description',
            'Level', 'Name', 'Description',
            'Level', 'Name', 'Description'
        ],
        [
            row[0][0], row[0][1], row[0][2],
            row[2][0], row[2][1], row[2][2],
            row[4][0], row[4][1], row[4][2],
            row[6][0], row[6][1], row[6][2]
        ],
        [
            row[1][0], row[1][1], row[1][2],
            row[3][0], row[3][1], row[3][2],
            row[5][0], row[5][1], row[5][2],
            row[7][0], row[7][1], row[7][2]
        ]
    ]

    return return_rows

# End: rpt_log_level()


def rpt_priority_hosts(db: clintosaurous.db.connect) -> list:

    """
    Generate priority messages counts by host.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select
            levels.level,
            pri.host,
            levels.name,
            pri.count,
            concat(pri.percentage, '%%') as percentage

        from syslog_host_priority_summary as pri

        inner join syslog_levels as levels
            on levels.level = pri.priority
            and levels.level <= 3

        where
            pri.datestamp = %s

        order by
            levels.level,
            pri.count desc,
            pri.host
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date])

    count = 0
    rpt_rows = [['Host', 'Priority', 'Count', '% of All']]
    for db_row in cursor:
        row = list(db_row)
        total_msgs = row[3]
        row[3] = f'{row[3]:,}'
        count += 1
        level = row[0]
        del row[0]
        form_txt = f"""
            <form method="put"
                enctype="multipart/form-data" name="host_level{count}">
            <input type="hidden" name="date" value="{rpt_date}" />
            <input type="hidden" name="host" value="{row[0]}" />
            <input type="hidden" name="level" value="{level}" />
            <input type="hidden" name="page" value="1" />
            <input type="hidden" name="total_msgs" value="{total_msgs}" />
            <input type="submit" name="host_level" value="View" />
        """
        form_txt += '</form>\n'
        row.append(form_txt)
        rpt_rows.append(row)

    cursor.close()

    return rpt_rows

# End: rpt_priority_hosts()


def rpt_priority_summary(db: clintosaurous.db.connect) -> list:

    """
    Generate summary of messages per log level.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = 'select level, name from syslog_levels order by level'
    cursor = db.cursor()
    cursor.execute(sql)
    levels = cursor.fetchall()
    cursor.close()

    sql = """
        select
            levels.level,
            levels.name,
            pri.count,
            concat(pri.percentage, '%%') as percentage

        from syslog_levels as levels

        left join syslog_priority_summary as pri
            on pri.priority = levels.level

        where
            pri.datestamp = %s

        order by
            levels.level
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date])

    level_data = {}
    for db_row in cursor:
        level_data[int(db_row[0])] = {
            "name": db_row[1],
            "count": db_row[2],
            "percentage": db_row[3]
        }

    for row in levels:
        level = int(row[0])

        try:
            level_data[level]
        except KeyError:
            level_data[level] = {
                "name": row[1],
                "count": 0,
                "percentage": '0.00%'
            }

    count = 0
    for level in level_data.keys():
        count += 1
        level_data[level]["html"] = f"""
            <form method="put"
                enctype="multipart/form-data" name="levels{count}">
            <input type="hidden" name="date" value="{rpt_date}" />
            <input type="hidden" name="level" value="{level}" />
            <input type="hidden" name="page" value="1" />
            <input type="hidden" name="total_msgs"
                value="{level_data[level]['count']}" />
            <input type="submit" name="levels" value="View" />
        """
        level_data[level]["count"] = f'{level_data[level]["count"]:,}'
        level_data[level]["html"] += '</form>\n'

    return_rows = [
        [
            'Priority', 'Count', '% of All', '',
            'Priority', 'Count', '% of All'
        ],
        [
            level_data[0]["name"], level_data[0]["count"],
            level_data[0]["percentage"], level_data[0]["html"],
            level_data[4]["name"], level_data[4]["count"],
            level_data[4]["percentage"], level_data[4]["html"]
        ],
        [
            level_data[1]["name"], level_data[1]["count"],
            level_data[1]["percentage"], level_data[1]["html"],
            level_data[5]["name"], level_data[5]["count"],
            level_data[5]["percentage"], level_data[5]["html"]
        ],
        [
            level_data[2]["name"], level_data[2]["count"],
            level_data[2]["percentage"], level_data[2]["html"],
            level_data[6]["name"], level_data[6]["count"],
            level_data[6]["percentage"], level_data[6]["html"]
        ],
        [
            level_data[3]["name"], level_data[3]["count"],
            level_data[3]["percentage"], level_data[3]["html"],
            level_data[7]["name"], level_data[7]["count"],
            level_data[7]["percentage"], level_data[7]["html"]
        ]
    ]

    return return_rows

# End: rpt_priority_summary()


def rpt_top_host_processes(db: clintosaurous.db.connect) -> list:

    """
    Generate top syslog message processes by host report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select host, process, count, concat(percentage, '%%')
        from syslog_host_process_summary
        where datestamp = %s
        order by count desc, host, process
        limit %s
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date, top_count])

    count = 0
    rpt_rows = [['Host', 'Process', 'Count', '% of All']]
    for db_row in cursor:
        row = list(db_row)
        count += 1
        form_txt = f"""
            <form method="put"
                enctype="multipart/form-data" name="host_process{count}">
            <input type="hidden" name="date" value="{rpt_date}" />
            <input type="hidden" name="host" value="{row[0]}" />
            <input type="hidden" name="page" value="1" />
            <input type="hidden" name="process" value="{row[1]}" />
            <input type="hidden" name="total_msgs" value="{row[2]}" />
            <input type="submit" name="host_process" value="View" />
        """
        form_txt += '</form>\n'
        rpt_rows.append(row)

        row[2] = f'{row[2]:,}'

    cursor.close()

    return rpt_rows

# End: rpt_top_host_processes()


def rpt_top_process_counts(db: clintosaurous.db.connect) -> list:

    """
    Generate top processes of all syslog messages report.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    sql = """
        select process, count, concat(percentage, '%%')
        from syslog_process_summary
        where datestamp = %s
        order by count desc, process
        limit %s
    """
    cursor = db.cursor()
    cursor.execute(sql, [rpt_date, top_count])

    count = 0
    rpt_rows = [['Process', 'Count', '% of All']]
    for db_row in cursor:
        row = list(db_row)
        count += 1
        form_txt = f"""
            <form method="put" action="syslog.cgi"
                enctype="multipart/form-data" name="processes{count}">
            <input type="hidden" name="date" value="{rpt_date}" />
            <input type="hidden" name="page" value="1" />
            <input type="hidden" name="process" value="{row[0]}" />
            <input type="hidden" name="total_msgs" value="{row[1]}" />
            <input type="submit" name="processes" value="View" />
        """
        form_txt += '</form>\n'
        rpt_rows.append(row)

        row[1] = f'{row[1]:,}'

    cursor.close()

    return rpt_rows

# End: rpt_top_process_counts()


def syslog_view(db: clintosaurous.db.connect) -> bool:

    """
    Display syslog messages for a host based on web form criteria.
    """

    # Type hints.
    if not isinstance(db, clintosaurous.db.connect):
        raise TypeError(
            f'db expected `clintosaurous.db.connect`, received {type(db)}')

    log_levels = ['EMR', 'ALR', 'CRI', 'ERR', 'WRN', 'LOG', 'INF', 'DBG']

    total_msgs = cgi.form_values.getvalue("total_msgs")
    if total_msgs is None:
        return False
    total_msgs = int(total_msgs)

    page, page_cnt, per_page, start_record = parse_page(total_msgs)
    hidden_values = {
        "date": rpt_date,
        "page": page,
        "total_msgs": total_msgs
    }
    where_values = [start_time, end_time]

    host = cgi.form_values.getvalue("host")
    if host is not None:
        hidden_values["host"] = host

    if cgi.form_values.getvalue("level") is not None:
        level = int(cgi.form_values.getvalue("level"))
        hidden_values["level"] = level
        if host is not None:
            title = f'Host {host} Priority {log_levels[level]}'
            where = """
                and (dev.hostname = %s or dev.display = %s)
                and sl.level = %s
            """
            where_values.append(host)
            where_values.append(host)
            where_values.append(level)
        else:
            title = f'Priority {log_levels[level]}'
            where = "and sl.level = %s"
            where_values.append(level)

    elif cgi.form_values.getvalue("host_process") is not None:
        process = cgi.form_values.getvalue("host_process")
        hidden_values["host_process"] = process
        title = f'Host {host} Process {process}'
        where = """
            and (dev.hostname = %s or dev.display = %s)
            and sl.program = %s
        """
        where_values.append(host)
        where_values.append(host)
        where_values.append(process)

    elif cgi.form_values.getvalue("levels") is not None:
        level = int(cgi.form_values.getvalue("levels"))
        hidden_values["levels"] = level
        title = f'Priority {log_levels[level]}'
        where = 'and sl.level = %s'
        where_values.append(level)

    elif cgi.form_values.getvalue("per_host") is not None:
        per_host = cgi.form_values.getvalue("per_host")
        hidden_values["per_host"] = per_host
        title = f'Host {host}'
        where = 'and (dev.hostname = %s or dev.display = %s)'
        where_values.append(host)
        where_values.append(host)

    elif cgi.form_values.getvalue("processes") is not None:
        process = cgi.form_values.getvalue("process")
        title = 'Process {process}'
        where = 'and sl.program = %s'
        where_values.append(process)

    else:
        return False

    where_values.append(start_record)
    where_values.append(per_page)
    sql = f"""
        select
            sl.timestamp,
            case
                when dev.display is not null then dev.display
                else dev.hostname
            end as hostname,
            case
                when sl.level = 0 then 'EMR'
                when sl.level = 1 then 'ALR'
                when sl.level = 2 then 'CRI'
                when sl.level = 3 then 'ERR'
                when sl.level = 4 then 'WRN'
                when sl.level = 5 then 'LOG'
                when sl.level = 6 then 'INF'
                when sl.level = 7 then 'DBG'
                else 'Unknown'
            end as level,
            sl.program,
            sl.msg

        from librenms.syslog as sl

        inner join librenms.devices as dev
            on dev.device_id = sl.device_id

        where
            timestamp between %s and %s
            {where}

        order by
            timestamp desc

        limit %s, %s
    """

    cursor = db.cursor()
    cursor.execute(sql, where_values)

    rpt_rows = [['Timestamp', 'Host', 'Log Level', 'Process', 'Message']]
    rpt_rows = [list(db_row) for db_row in cursor]
    rpt_rows.insert(
        0, ['Timestamp', 'Host', 'Log Level', 'Process', 'Message'])

    cursor.close()

    print(cgi.hr())
    print(cgi.text_box(cgi.table(rpt_rows), title))

    form_txt = '<form action="syslog.cgi" name="page_select" method="put">\n'
    for key in sorted(hidden_values.keys()):
        form_txt += (
            f'<input type="hidden" name="{key}" ' +
            f'value="{hidden_values[key]}">\n'
        )
    form_txt += page_buttons(page, page_cnt, total_msgs)

    print(form_txt)

    return True

# End: syslog_view()


if __name__ == '__main__':
    cgi = clintosaurous.cgi.cgi(
        title='syslog Reports',
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

    top_count = 25

    user, passwd = credentials.data().get('mysql-report_ro')
    db = clintosaurous.db.connect(
        host='mysql1.clintosaurous.com',
        user=user,
        passwd=passwd,
        database='reports',
        logging=False
    )

    form_opts = form_options(db)
    print(cgi.form(**form_opts))
    if not display_trending(db) and not syslog_view(db):
        display_report(db)

    db.close()

    print(cgi.end_page())
