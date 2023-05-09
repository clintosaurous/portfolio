#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
Web form for root web menu.
"""


import clintosaurous.cgi
import os
import yaml


VERSION = '2.0.0'
LAST_UPDATE = '2022-10-19'


if __name__ == '__main__':
    cgi = clintosaurous.cgi.cgi(
        title='Temp Title',
        version=VERSION,
        last_update=LAST_UPDATE,
        copyright=2022
    )

    etc_dir = '/etc/clintosaurous/www'
    conf_file = cgi.form_values.getvalue('conf')
    if conf_file is not None and conf_file:
        conf_file = f'{conf_file}.yaml'
    else:
        conf_file = 'root.yaml'
    conf_path = os.path.join(etc_dir, conf_file)
    with open(conf_path, newline='') as c:
        conf = yaml.safe_load(c)

    cgi.title = conf["title"]
    print(cgi.start_page())
    if cgi.header:
        print(cgi.hr())

    print(cgi.index_list(conf["links"]))

    print(cgi.end_page())
