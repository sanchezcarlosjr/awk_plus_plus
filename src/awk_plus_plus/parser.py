from sqlmesh.core.dialect import parse
from sqlmesh.core.macros import MacroEvaluator, macro


@macro()
def schema(evaluator: MacroEvaluator, url: str) -> str:
    return f"""'{{"url": "{url}"}}'"""


@macro()
def s(evaluator: MacroEvaluator, value: str) -> str:
    return f"'{value}'"


@macro()
def grep(evaluator: MacroEvaluator, expression: str) -> str:
    return f"SELECT * FROM object_directory where name ILIKE '%' || '{expression}' || '%'"


class SQLTemplate:
    def __init__(self, template: str, dialect: str = "duckdb"):
        self.template = template
        self.dialect = dialect
        self.evaluator = MacroEvaluator(dialect=dialect)

    def render(self, **kwargs) -> str:
        expressions = parse(self.template)
        x = "; ".join(
            map(
                lambda expression: self.evaluator.transform(expression).sql(),
                expressions,
            )
        )
        return x
