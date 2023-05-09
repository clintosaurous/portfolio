#!/opt/clintosaurous/venv/bin/python3 -Bu

""" Functions for e-mail services. """


from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename
import smtplib


VERSION = '1.1.0'
LAST_UPDATE = "2022-09-28"


def send(
    to_addr='Clint <clint@clintosaurous.com>',
    from_addr='Clint <clint@clintosaurous.com>',
    subject=None, text=None,
    attachments=[], server='localhost', html=True
):

    """
    Send an e-mail using the supplied dictionary of options.

    `to`: E-Mail address(es) to send to. Comma separated. Default:
    clint@clintosaurous.com.

    `from`: E-Mail address to send e-mail from. Default:
    clint@clintosaurous.com.

    `subject`: E-Mail subject.

    `text`: E-Mail text.

    `attachments`: List of files to attach to the e-mail.

    `server`: Name or IP of SMTP server to connect to. Default: localhost

    `html`: Boolean of if text is HTML. Default to not HTML.
    """

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    if html:
        msg.attach(MIMEText(text, "html"))
    else:
        msg.attach(MIMEText(text))

    for file_name in attachments:
        with open(file_name, "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=basename(file_name)
            )
        # After the file is closed
        part['Content-Disposition'] = \
            f'attachment; filename="{basename(file_name)}"'
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(from_addr, to_addr, msg.as_string())
    smtp.close()

# End send()
