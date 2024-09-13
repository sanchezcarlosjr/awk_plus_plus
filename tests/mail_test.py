from awk_plus_plus.plugin_manager import plugin_manager
import pandas as pd
from awk_plus_plus.actions import interpret_url

def test_read_mail():
    results = plugin_manager.hook.read(url=interpret_url("imap://{{keyring.awk_plus_plus.email}}:{{keyring.awk_plus_plus.primary_email_password}}@imap.gmail.com?folder=INBOX&limit=10"))
    assert len(results) > 0
