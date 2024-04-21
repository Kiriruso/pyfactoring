class Scope:
    def __init__(self, outer: "Scope" = None):
        self.variables = {}
        if outer:
            self.variables = {name: template for name, template in outer.variables.items()}

    def var(self, id_: str) -> str:
        if id_ in self.variables.values():
            return id_
        if id_ not in self.variables:
            self.variables[id_] = f"__var_{len(self.variables)}__"
        return self.variables[id_]
