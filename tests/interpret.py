from awk_plus_plus.plugin_manager import plugin_manager
import pandas as pd
import keyring
from awk_plus_plus.interpreter.interpreter import interpret
import awk_plus_plus
import sys

def test_connect_to_keyring():
    keyring.set_password('awk_plus_plus', 'x', 'y')
    result = interpret("keyring://backend/awk_plus_plus/x")
    assert result == "y"

@awk_plus_plus.hook_implementation
def read(url):
   return "x"

def test_intercept_url():
    plugin_manager.register(sys.modules[__name__])
    result = interpret("adhoc://read/")
    assert result == "x"
