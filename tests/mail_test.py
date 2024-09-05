from awk_plus_plus.url_action import MailReader
import pandas as pd

def test_read_mail():
    mr = MailReader()
    df = mr.read("imap://EMAIL:APP PASSWORD@imap.gmail.com?folder=INBOX&limit=10")
    print(df)
    assert df is None
