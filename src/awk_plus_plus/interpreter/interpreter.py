from kink import di
import re
from awk_plus_plus.plugin_manager import plugin_manager
from awk_plus_plus import _logger
import urllib
import sys
import _jsonnet
from datetime import datetime
import duckdb as db
import pandas as pd
import json
from duckdb.typing import VARCHAR
import os
import jq


def interpret(url: str):
    parsed_result = urllib.parse.urlparse(url.strip())
    results = plugin_manager.hook.read(url=parsed_result)
    if results is None or len(results) == 0:
        return None
    if len(results) == 1:
        return results[0]
    return results


def eval_jq(json_str: str, expression: str):
    return jq.compile(expression).input_text(json_str).text()


def serializer(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient='records')
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return json.JSONEncoder().default(obj)


def create_connection(name):
    def connect():
        connection = db.connect(name, config={'threads': 10})
        try:
            connection.create_function('interpret', interpret_url, [VARCHAR], VARCHAR, exception_handling="return_null")
        except Exception as e:
            pass
        return connection

    connection = connect()
    connection.sql("""
                    INSTALL json;
                    LOAD json;
                    INSTALL https;
                    LOAD https;
                    INSTALL excel;
                    LOAD excel;
                    INSTALL spatial;
                    LOAD spatial;
                """)
    return connect


native_callbacks = {
    'interpret': (('url',), interpret),
    'i': (('url',), interpret)
}


def evaluate(expression: str, db_name: str = ":memory:"):
    connect = create_connection(db_name)
    di['db_name'] = db_name
    di.factories['db_connection'] = lambda di: connect()
    expression = os.path.isfile(expression) and open(expression).read() or expression
    header = 'local interpret = std.native("interpret"); local i = std.native("i");'
    try:
      json_str = _jsonnet.evaluate_snippet("snippet", header+expression, ext_vars={'start_time': str(datetime.now())}, native_callbacks=native_callbacks)
    except Exception as e:
      _logger.warn(e)
      json_str = _jsonnet.evaluate_snippet("snippet", header+"'"+expression+"'", ext_vars={'start_time': str(datetime.now())}, native_callbacks=native_callbacks)
    return json.loads(json_str)

