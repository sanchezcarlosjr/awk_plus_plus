import os
import urllib

import awk_plus_plus
from awk_plus_plus.io.assets import read_from
import imaplib
import email
from email.header import decode_header
import pandas as pd
import re


class FileReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: str):
        url = urllib.parse.urlparse(url).path
        filename = os.path.basename(url).replace("-", "_").replace(".", "_")
        result = read_from(url)
        result['source_file'] = url
        return result


class MailReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: str):
        result = urllib.parse.urlparse(url)
        result.query = result.query.replace("+", " ")
        netloc_matches = re.match('(?P<user>.+):(?P<password>.+)@(?P<host>.+)', result.netloc)
        mail = imaplib.IMAP4_SSL(netloc_matches.group('host'))
        mail.login(netloc_matches.group('user'), netloc_matches.group('password'))

        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        subjects = []
        senders = []
        bodies = []

        for email_id in email_ids[-20:]:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    from_ = msg.get("From")

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

        # Create a DataFrame
        email_data = pd.DataFrame({
            "Subject": subjects,
            "Sender": senders,
            "Body": bodies
        })

        # Logout from the server
        mail.logout()

        # Return the DataFrame
        return email_data