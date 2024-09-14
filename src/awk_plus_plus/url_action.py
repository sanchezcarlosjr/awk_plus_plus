import os
import urllib
from urllib.parse import ParseResult

import awk_plus_plus
from awk_plus_plus.io.assets import read_from
import imaplib
import email
from email.header import decode_header
import pandas as pd
import re
from awk_plus_plus import _logger as logger
import hashlib

class FileReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: ParseResult):
        if url.scheme != "file" and url.scheme != "":
            return None
        filename = re.sub(r"-|\.| ", "_", os.path.basename(url.path).lower())
        result = read_from(url.path)
        result['source'] = url.path
        return {
            'normalized_name': filename
        }, result


class MailReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: ParseResult):
        if url.scheme != "imap":
            return None
        netloc_matches = re.match('(?P<user>.+):(?P<password>.+)@(?P<host>.+)', url.netloc)
        if netloc_matches is None:
            logger.debug("Invalid IMAP URL")
            return None
        limit = int(-10 if (x:=re.match("limit=(-?[0-9]+)", url.query)) is None else x.group(1))
        mail = imaplib.IMAP4_SSL(netloc_matches.group('host'))
        mail.login(netloc_matches.group('user'), netloc_matches.group('password'))

        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        normalized_name = hashlib.sha256(url.geturl().encode('utf-8')).hexdigest()[0:5]

        subjects = []
        senders = []
        recipients = []
        cc_list = []
        bcc_list = []
        bodies = []
        dates = []

        for email_id in email_ids[limit:]:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    from_ = msg.get("From")
                    to_ = msg.get("To")
                    cc_ = msg.get("CC")
                    bcc_ = msg.get("BCC")
                    date_ = msg.get("Date")

                    try:
                        date_parsed = email.utils.parsedate_to_datetime(date_)
                    except:
                        date_parsed = date_

                    body = ""

                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                   body = part.get_payload(decode=True).decode(errors='replace')
                                except:
                                    body = part.get_payload()
                                   
                    else:
                        body = msg.get_payload(decode=True).decode()

                    subjects.append(subject)
                    senders.append(from_)
                    bodies.append(body)
                    recipients.append(to_)
                    cc_list.append(cc_)
                    bcc_list.append(bcc_)
                    dates.append(date_parsed)

        # Create a DataFrame
        email_data = pd.DataFrame({
            "Subject": subjects,
            "Sender": senders,
            "Recipient": recipients,
            "CC": cc_list,
            "BCC": bcc_list,
            "Body": bodies,
            "Date": dates,
            'source': normalized_name
        })

        mail.logout()

        return {
            'normalized_name': normalized_name
        }, email_data
