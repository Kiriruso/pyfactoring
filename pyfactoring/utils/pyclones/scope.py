class Scope:
    __slots__ = ["is_local", "is_global", "_variables", "_constants", "_imports", "_locals"]

    COMMON_KEYWORDS = ("self", "cls", "_")

    def __init__(self, outer: "Scope" = None, *, global_: bool = False):
        self.is_local: bool = False
        self.is_global: bool = global_

        self._variables: dict[str, str] = {}
        self._constants: dict[str, str] = {}
        self._imports: set[str] = set()
        self._locals: dict[str, str] = {}

        if outer:
            self.is_local = True and not outer.is_global
            self._locals = outer._locals if not outer.is_global else {}
            self._variables = {name: template for name, template in outer._variables.items()}
            self._constants = outer._constants if not outer.is_global else {}
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

    def update_imports(self, imports: list[str]):
        self._imports.update(imports)

    def clear_imports(self):
        self._imports.clear()

    def get_name(self, id_: str) -> str:
        if id_ in self.COMMON_KEYWORDS or id_ in self._imports:
            return id_

        if not self.is_global and id_ in self._locals.values():
            return id_

        if id_ in self._variables.values():
            return id_

        if not self.is_global and self.is_local and id_ not in self._variables.keys():
            if id_ not in self._locals:
                self._locals[id_] = f"__local_{len(self._locals)}__"
            return self._locals[id_]

        if id_ not in self._variables:
            self._variables[id_] = f"__var_{len(self._variables)}__"
        return self._variables[id_]

    def get_const(self, value_) -> str:
        if value_ == Ellipsis:
            return Ellipsis

        value_ = str(value_)

        if value_ in self._constants.values():
            return value_

        if value_ not in self._constants:
            self._constants[value_] = f"__const_{len(self._constants)}__"
        return self._constants[value_]
