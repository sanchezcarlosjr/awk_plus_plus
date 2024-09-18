from rich.console import Console
from awk_plus_plus import __version__, setup_logging, _logger
import typer
from typing import Optional, List
from typing_extensions import Annotated
import json
from kink import di
from typing import Tuple
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
def run_webservice(
        share: Annotated[bool, typer.Option(help="Share with Gradio servers.")] = False,
        default_concurrency_limit: Annotated[int, typer.Option(help="Default concurrency limit.")] = 40,
        basic_auth_user: Annotated[List[str], typer.Option(help="Define your basic auth user with the format: username:password")] = None,
        exclusive_expression: Annotated[str, typer.Option(help="Every time someone call your service, we call it with this expression. It can be an inline expression or a file.")] = None):
    _logger.info("Starting webapp..")
    di['exclusive_expression'] = exclusive_expression
    users = [tuple(user.split(":")) for user in basic_auth_user] if basic_auth_user else None
    from awk_plus_plus.webapp import demo
    demo.queue(default_concurrency_limit=default_concurrency_limit)
    demo.launch(share=share, auth=users)



def main(verbose: Optional[int] = typer.Option(0, '--verbose', '-v', count=True,
                                               help="Increase verbosity by augmenting the count of 'v's, and enhance "
                                                    "the total number of messages.")):
    setup_logging(verbose * 10)
    app()


def run():
    app()


if __name__ == "__main__":
    typer.run(app)
