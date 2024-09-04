import awk_plus_plus


class SQLFunction:
    def __init__(self):
        self.name = "sql_function"

    @awk_plus_plus.hook_implementation
    def function(self, connection):
        connection.create_function(self.name, f, [VARCHAR, VARCHAR], VARCHAR, exception_handling="return_null")
        return self.name
