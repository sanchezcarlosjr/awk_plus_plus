import os.path
import urllib.parse
from datetime import datetime

import _jsonnet
import duckdb as db
import jq
from dask.threaded import get
from duckdb.typing import VARCHAR
from rich.console import Console
from awk_plus_plus import __version__, setup_logging, _logger
from awk_plus_plus.actions import interpret_url
from awk_plus_plus.io.assets import pd, read_from
from awk_plus_plus.parser import SQLTemplate
import keyring

__author__ = "sanchezcarlosjr"
__copyright__ = "sanchezcarlosjr"
__license__ = "MIT"

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.

import typer
import os
import getpass
from typing import Optional, List
from typing_extensions import Annotated
import json
from urllib.parse import ParseResult
from kink import di, inject

from awk_plus_plus.io.http import post, http_get
from awk_plus_plus.parser import SQLTemplate

app = typer.Typer()


@app.command()
def version():
    print(f"awk_plus_plus {__version__}")




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

import sys
native_callbacks = {
    'interpret': (('url',), interpret_url)
}


@app.command("i", help="Interpret an expression from a file or a string. interpret alias")
@app.command("interpret",help="""
Interpret an expression. Example:
cti interpret '{"x": std.format("sql:SELECT * FROM %s", self.z), "z": "dataset", "exec_time": std.extVar("start_time")}'
""")
def interpret(expression: str,
              verbose: Annotated[int, typer.Option("-v", help="Describe the verbosity.")] = 3,
              pretty: Annotated[bool, typer.Option("-p", help="Pretty print.")] = False,
              db_name: Annotated[str, typer.Option(help="Database filename. If you wish to run the database in memory, you have to write it as :memory:")] = "db.sql"):
    setup_logging(verbose * 10)
    connect = create_connection(db_name)
    di['db_name'] = db_name
    di.factories['db_connection'] = lambda di: connect()
    expression = os.path.isfile(expression) and open(expression).read() or expression
    header = 'local interpret = std.native("interpret");'
    try:
      json_str = _jsonnet.evaluate_snippet("snippet", header+expression, ext_vars={'start_time': str(datetime.now())}, native_callbacks=native_callbacks)
    except Exception as e:
      _logger.warn(e)
      json_str = _jsonnet.evaluate_snippet("snippet", header+"'"+expression+"'", ext_vars={'start_time': str(datetime.now())}, native_callbacks=native_callbacks)
    json_obj = json.loads(json_str)
    console = Console()
    if pretty:
        console.print_json(json.dumps(json_obj, indent=4, default=serializer))
    else:
        print(json.dumps(json_obj, default=serializer))
    return json_obj



@app.command()
def run_demo(share: Annotated[bool, typer.Option(help="Share with Gradio servers.")] = False):
    _logger.info("Starting webapp..")
    from awk_plus_plus.webapp import demo
    demo.launch(share=share)


def predict(file: str):
    _logger.info("Prediction...")


def write_systemd_service(service_name, description, exec_start, working_directory='/', after='network.target',
                          restart='on-failure', restart_sec=5, service_file_dir='/etc/systemd/system'):
    """
    Create a systemd service unit file.

    Parameters:
    - service_name: Name of the service (e.g., 'my_service')
    - description: Description of the service
    - exec_start: Command to start the service
    - working_directory: Working directory for the service (default is '/')
    - after: Dependencies to start after (default is 'network.target')
    - restart: Restart policy (default is 'on-failure')
    - restart_sec: Delay before restarting (default is 5 seconds)
    - service_file_dir: Directory to place the service file (default is '/etc/systemd/system')
    """
    service_file_path = os.path.join(service_file_dir, f'{service_name}.service')
    user = getpass.getuser()  # Get the current user

    service_content = f"""[Unit]
Description={description}
After={after}

[Service]
ExecStart={exec_start}
WorkingDirectory={working_directory}
User={user}
Restart={restart}
RestartSec={restart_sec}
Type=simple

[Install]
WantedBy=multi-user.target
"""

    try:
        with open(service_file_path, 'w') as service_file:
            service_file.write(service_content)
        print(f"Service file '{service_file_path}' created successfully.")

        # Reload systemd manager configuration
        os.system('systemctl daemon-reload')

        # Enable the service to start on boot
        os.system(f'systemctl enable {service_name}.service')

        # Start the service
        os.system(f'systemctl start {service_name}.service')

        print(f"Service '{service_name}' started successfully.")

    except Exception as e:
        print(f"An error occurred while creating the service file: {e}")


@app.command()
def create_service(exec_start: Annotated[str, typer.Option(help="Command to start the service")],
                   working_directory: Annotated[
                       str, typer.Option(help="Working directory for the service", default='/')] = '/',
                   after: Annotated[str, typer.Option(help="Dependencies to start after",
                                                      default='network.target')] = 'network.target',
                   restart: Annotated[str, typer.Option(help="Restart policy", default='on-failure')] = 'on-failure',
                   service_file_dir: Annotated[str, typer.Option(help="Directory to place the service file",
                                                                 default='/etc/systemd/system')] = '/etc/systemd/system'):
    """
    Command to create a systemd service unit file.
    """
    # Suggested exec_start commands
    suggestions = [f"conda run -n {__name__} {__name__} run_webservice", f"{__name__} run_webservice"]

    print("Here are some suggestions for the ExecStart command:")
    for suggestion in suggestions:
        print(f"  - {suggestion}")

    exec_start = typer.prompt("Please enter the ExecStart command", default=suggestions[0])

    write_systemd_service("awk_plus_plus", "Add a short description here!", exec_start, working_directory, after,
                          restart, 5, service_file_dir)


def main(verbose: Optional[int] = typer.Option(0, '--verbose', '-v', count=True,
                                               help="Increase verbosity by augmenting the count of 'v's, and enhance "
                                                    "the total number of messages.")):
    setup_logging(verbose * 10)
    app()


def run():
    app()


if __name__ == "__main__":
    typer.run(app)
