import os
import urllib
from urllib.parse import ParseResult, parse_qs

import awk_plus_plus
from awk_plus_plus.io.assets import read_from
import imaplib
import email
from email.header import decode_header
import pandas as pd
import re
from awk_plus_plus import _logger as logger
import hashlib
import keyring
from kink import di
import duckdb
from awk_plus_plus.io.http import post, http_get, download
from pathlib import Path
import sys

class FileReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: ParseResult):
        if url.scheme.lower() != "file" and url.scheme != "":
            return None
        db = di['db_connection']
        filename = re.sub(r"-|\.| ", "_", os.path.basename(url.path).lower())
        result = read_from(url.path)
        result['source'] = url.path
        return result.to_dict('records')

class Sql:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: ParseResult):
        if url.scheme.lower() != "sql":
            return None
        db = di['db_connection']
        sql = url.path.replace("`", "'")
        return db.sql(sql).to_df().to_dict('records')



class Keyring:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: ParseResult):
        if url.scheme.lower() != "keyring":
            return None
        backend = url.netloc
        path = url.path.split("/")
        service = path[1]
        key = path[2]
        return keyring.get_password(service, key)


class Stream:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: ParseResult):
        netlocs = {'stdin': sys.stdin}
        if url.scheme.lower() != "stream" or url.netloc.lower() not in netlocs:
            return None
        queries = parse_qs(url.query)
        transform = lambda x: x
        if 'strip' in queries:
            transform = lambda x: x.strip()
        lines = []
        for line in netlocs.get(url.netloc, sys.stdin):
            lines.append(transform(line))
        return lines
class Http:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: ParseResult):
        scheme = url.scheme.lower()
        if scheme != "http" and scheme != "https":
            return None
        queries = parse_qs(url.query)
        if 'awk_download' in queries:
             path = Path(queries['awk_download'][0])
             path.parent.mkdir(parents=True, exist_ok=True)
             try:
               return download(url.geturl(), str(path))
             except Exception as e:
               logger.error(e)
               return path
        return http_get(url.geturl(), json_decode=True)

class MailReader:
    """A hook implementation namespace."""

    @awk_plus_plus.hook_implementation
    def read(self, url: ParseResult):
        if url.scheme.lower() != "imap":
            return None
        netloc_matches = re.match('(?P<user>.+):(?P<password>.+)@(?P<host>.+)', url.netloc)
        if netloc_matches is None:
            logger.debug("Invalid IMAP URL")
            return None

        db: duckdb.DuckDBPyConnection = di['db_connection']
        limit = int(-10 if (x:=re.match("limit=(-?[0-9]+)", url.query)) is None else x.group(1))
        mail = imaplib.IMAP4_SSL(netloc_matches.group('host'))
        mail.login(netloc_matches.group('user'), netloc_matches.group('password'))

        mail.select("inbox")

        status, messages = mail.search(None, "ALL")
        email_ids = messages[0].split()

        normalized_name = hashlib.sha256(url.geturl().encode('utf-8')).hexdigest()[0:6]
        db.execute(f"""
            CREATE TABLE IF NOT EXISTS '{normalized_name}' (
                subject TEXT,
                sender TEXT,
                recipient TEXT,
                cc TEXT,
                bcc TEXT,
                body TEXT,
                date TEXT
            )
        """)

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


                query = f"""
                 INSERT INTO '{normalized_name}' (subject, sender, recipient, cc, bcc, body, date)
                 VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                values = (subject, from_, to_, cc_, bcc_, body, date_)
                db.execute(query, values)


        mail.logout()

        return normalized_name


