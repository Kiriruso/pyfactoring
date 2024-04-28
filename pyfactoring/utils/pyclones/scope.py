class Scope:
    __slots__ = ["_variables", "_constants", "_imports", "_locals"]

    def __init__(self, outer: "Scope" = None):
        self._variables: dict[str, str] = {}
        self._constants: dict[str, str] = {}
        self._imports: set[str] = set()
        self._locals: dict[str, str] = {}

        if outer:
            self._variables = {name: template for name, template in outer._variables.items()}
            self._constants = outer._constants
            self._imports = outer._imports

    @property
    def variables(self) -> list[str]:
        return self._variables.keys()

    @property
    def constants(self) -> list[str]:
        return self._constants.keys()

    @property
    def imports(self) -> set[str]:
        return self._imports

    @property
    def locals(self) -> list[str]:
        return self._locals.keys()

    def add_import(self, import_name: str):
        self._imports.add(import_name)

    def variable(self, id_: str) -> str:
        if id_ in self._imports or id_ in self._variables.values():
            return id_

        if id_ not in self._variables:
            self._variables[id_] = f"__var_{len(self._variables)}__"

        return self._variables[id_]

    def const(self, value_) -> str:
        if value_ == Ellipsis:
            return Ellipsis

        value_ = str(value_)

        if value_ in self._constants.values():
            return value_

        if value_ not in self._constants:
            self._constants[value_] = f"__const_{len(self._constants)}__"

        return self._constants[value_]

    def local(self, name_: str) -> str:
        if name_ in self._imports:
            return name_

        if name_ not in self._locals:
            self._locals[name_] = f"__local_{len(self._locals)}__"

        return self._locals[name_]
