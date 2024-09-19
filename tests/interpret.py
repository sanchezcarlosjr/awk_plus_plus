from awk_plus_plus.plugin_manager import plugin_manager
import pandas as pd
import keyring
from awk_plus_plus.interpreter.interpreter import interpret, create_connection
import awk_plus_plus
from kink import di
import sys

def test_connect_to_keyring():
    keyring.set_password('awk_plus_plus', 'x', 'y')
    result = interpret("keyring://backend/awk_plus_plus/x")
    assert result == "y"

@awk_plus_plus.hook_implementation
def read(url):
   if url.scheme != "adhoc":
      return None
   return "x"

def test_intercept_url():
    plugin_manager.register(sys.modules[__name__])
    result = interpret("adhoc://read/")
    assert result == "x"

def test_interpret_sql():
    db_name = 'db_name'
    connect = create_connection(db_name)
    di['db_name'] = db_name
    di.factories['db_connection'] = lambda di: connect()
    result = interpret("sql:SELECT 1 as result")
    assert result == [{"result": 1}]
