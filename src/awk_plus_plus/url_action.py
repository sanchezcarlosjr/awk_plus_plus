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

class FileReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: str):
        parsed_result : ParseResult = urllib.parse.urlparse(url)
        if parsed_result.scheme != "file" or not parsed_result.scheme != "":
            return None
        url = urllib.parse.urlparse(url).path
        filename = os.path.basename(url).replace("-", "_").replace(".", "_")
        result = read_from(url)
        result['source_file'] = url
        return {
            'normalized_name': filename
        }, result


class MailReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: str):
        result = urllib.parse.urlparse(url)
        if result.scheme != "imap":
            return None
        netloc_matches = re.match('(?P<user>.+):(?P<password>.+)@(?P<host>.+)', result.netloc)
        if netloc_matches is None:
            logger.debug("Invalid IMAP URL")
            return None
        limit = int(-10 if (x:=re.match("limit=(-?\d+)", result.query)) is None else x.group(1))
        mail = imaplib.IMAP4_SSL(netloc_matches.group('host'))
        mail.login(netloc_matches.group('user'), netloc_matches.group('password'))

        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

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

                    # Convert Date to a proper datetime object if needed
                    try:
                        date_parsed = email.utils.parsedate_to_datetime(date_)
                    except:
                        date_parsed = date_  # Fallback in case of parsing error

                    body = ""

                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
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
            "Date": dates
        })

        # Logout from the server
        mail.logout()

        # Return the DataFrame
        return {
            'normalized_name': 'email'
        }, email_data