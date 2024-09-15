import numbers
from venv import logger
from kink import inject
import re
from awk_plus_plus.plugin_manager import plugin_manager
import urllib


def interpret_url(url: str):
    url = urllib.parse.urlparse(url)
    results = plugin_manager.hook.read(url=url)
    if results is None or len(results) == 0:
        return None
    return results[0]
