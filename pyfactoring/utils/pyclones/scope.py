class Scope:
    __slots__ = ["_variables", "_constants", "_imports"]

    def __init__(self, outer: "Scope" = None):
        self._variables: dict[str, str] = {}
        self._constants: dict[str, str] = {}
        self._imports: set[str] = set()

        if outer:
            self._variables = {name: template for name, template in outer._variables.items()}
            self._constants = outer._constants
            self._imports = outer._imports

    def add_import(self, import_name: str):
        self._imports.add(import_name)

    def scoped_variable(self, id_: str) -> str:
        if id_ in self._imports or id_ in self._variables.values():
            return id_

        if id_ not in self._variables:
            self._variables[id_] = f"__var_{len(self._variables)}__"

        return self._variables[id_]

    def scoped_constant(self, value_) -> str:
        if value_ == Ellipsis:
            return Ellipsis

        value_ = str(value_)

        if value_ in self._constants.values():
            return value_

        if value_ not in self._constants:
            self._constants[value_] = f"__const_{len(self._constants)}__"

        return self._constants[value_]
