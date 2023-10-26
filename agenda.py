# -*- coding: utf-8 -*-
#
# Retrieve agenda items for my classes for a specified day
# and send them via email.
#
# SAMPLE URL:
# https://web.spaggiari.eu/cvv/app/default/agenda.php?ope=get_events&mode=agenda&tutte_note=0&aula_id=undefined
# It's a POST, this is a sample form data:
# classe_id=1391771&gruppo_id=&start=2023-10-23&end=2023-10-30
#

from datetime import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from shared import *


def send_email(to: str, subject: str, body: str):
    """
    Send an email using the configuration parameters from settings.py.
    """
    if EMAIL_USE_TLS:
        smtp = smtplib.SMTP_SSL  # type: ignore
    else:
        smtp = smtplib.SMTP  # type: ignore
    with smtp(EMAIL_HOST, EMAIL_PORT) as server:
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = EMAIL_FROM
        message.attach(MIMEText(body, "plain"))
        message["To"] = to
        server.sendmail(EMAIL_FROM, to, message.as_string())


if __name__ == "__main__":
    now = datetime.now()
    start_date = now.strftime("%Y-%m-%d")
    #start_date = (now - timedelta(days=14)).strftime("%Y-%m-%d")
    end_date = (now + timedelta(days=7)).strftime("%Y-%m-%d")
    cv = ClasseViva(USERNAME, PASSWORD)
    agenda = []
    for class_id in [x for x in [s.class_id for s in cv.get_subjects()] + list(EXTRA_CLASS_IDS.keys()) if x]:
        agenda.extend(cv.get_agenda(start_date, end_date, AUTORE_ID, class_id, EXTRA_CLASS_IDS.get(class_id)))
    subject = f"Agenda dal {start_date} al {end_date}"
    body = "\n\n".join(str(ai) for ai in sorted(agenda, key=lambda x: x.start))
    send_email(EMAIL_TO, subject, body)