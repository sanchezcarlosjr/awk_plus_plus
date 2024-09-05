from awk_plus_plus.plugin_manager import plugin_manager
import pandas as pd

def test_read_with_plugins():
    results = plugin_manager.hook.read(url="imap://app:password@imap.gmail.com?folder=INBOX&limit=10")
    assert len(results) == 0
