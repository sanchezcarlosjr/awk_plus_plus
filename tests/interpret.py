from awk_plus_plus.plugin_manager import plugin_manager
import pandas as pd
import keyring
from awk_plus_plus.interpreter.interpreter import interpret

def test_connect_to_keyring():
    keyring.set_password('awk_plus_plus', 'x', 'y')
    result = interpret("keyring://backend/awk_plus_plus/x")
    assert result == "y"
