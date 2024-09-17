from rich.console import Console
from awk_plus_plus import __version__, setup_logging, _logger
import typer
from typing import Optional, List
from typing_extensions import Annotated
import json
from kink import di, inject
from awk_plus_plus.interpreter.interpreter import evaluate, serializer

__author__ = "sanchezcarlosjr"
__copyright__ = "sanchezcarlosjr"
__license__ = "MIT"

# ---- CLI ----
# The functions defined in this section are wrappers around the main Python
# API allowing them to be called directly from the terminal as a CLI
# executable/script.

app = typer.Typer()


@app.command()
def version():
    print(f"awk_plus_plus {__version__}")


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
    json_obj = evaluate(expression, db_name)
    console = Console()
    if pretty:
        console.print_json(json.dumps(json_obj, indent=4, default=serializer))
    else:
        print(json.dumps(json_obj, default=serializer))
    return json_obj



@app.command()
def run_webservice(share: Annotated[bool, typer.Option(help="Share with Gradio servers.")] = False):
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
