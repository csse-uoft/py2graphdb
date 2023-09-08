from abc import ABC, abstractmethod

class Operator(ABC):
    prop = None
    def __init__(self, prop) -> None:
        self.prop = prop
    
    @abstractmethod
    def to_sparql(self, var, val):
        pass

class eq(Operator):
    def to_sparql(self, var, val):
        return f"FILTER({var} = {val})"

class ne(Operator):
    def to_sparql(self, var, val):
        return f"FILTER({var} != {val})"

class le(Operator):
    def to_sparql(self, var, val):
        return f"FILTER({var} <= {val})"

class ge(Operator):
    def to_sparql(self, var, val):
        return f"FILTER({var} >= {val})"

class lt(Operator):
    def to_sparql(self, var, val):
        return f"FILTER({var} < {val})"

class gt(Operator):
    def to_sparql(self, var, val):
        return f"FILTER({var} > {val})"

class has(Operator):
    def to_sparql(self, var, val):
        clean_val = '(%s)' % ', '.join(map(str, val))
        return f"FILTER({var} IN {clean_val})"

class nothas(Operator):
    def to_sparql(self, var, val):
        clean_val = '(%s)' % ', '.join(map(str, val))
        return f"FILTER({var} NOT IN {clean_val})"
