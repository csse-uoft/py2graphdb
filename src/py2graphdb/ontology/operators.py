from abc import ABC, abstractmethod
import numpy as np
import string
ALPHABET = np.array(list(string.ascii_lowercase))
def generate_random_var(length=10):
    return ''.join(np.random.choice(ALPHABET, size=length))

class Operator(ABC):
    prop = None
    prop_str = None
    to_select_var = None
    def __init__(self, prop) -> None:
        self.prop = prop

    def set_normalized(self, prop_str):
        self.prop_str = prop_str

    def to_select(self, var, owner='s'):
        concat_var = f"{var}_OPERATOR_{type(self).__name__}"
        self.var = var
        self.to_select_var = concat_var
        return ''
    
    @abstractmethod
    def to_sparql(self, var, val, owner='s'):
        pass

class eq(Operator):
    def to_sparql(self, var, val, owner='s'):
        return f"FILTER({var} = {val})"

class ne(Operator):
    def to_sparql(self, var, val, owner='s'):
        return f"FILTER({var} != {val})"

class le(Operator):
    def to_sparql(self, var, val, owner='s'):
        return f"FILTER({var} <= {val})"

class ge(Operator):
    def to_sparql(self, var, val, owner='s'):
        return f"FILTER({var} >= {val})"

class lt(Operator):
    def to_sparql(self, var, val, owner='s'):
        return f"FILTER({var} < {val})"

class gt(Operator):
    def to_sparql(self, var, val, owner='s'):
        return f"FILTER({var} > {val})"

class has_filter(Operator):
    def to_sparql(self, var, val, owner='s'):
        clean_val = '(%s)' % ', '.join(map(str, val))
        return f"FILTER({var} IN {clean_val})"

class hasany(has_filter):
    """
    Same filter as has_filter(), but used for disjunction conjunction in query
    """
    pass
class has(hasany):
    """
    Same filter as hasany(). Serves as a temporary place holder

    """
    pass
class hasall(has_filter):
    """
    Same filter as has_filter(), but used for conjunction condition in query
    """
    def to_select(self, var, separator='###'):
        concat_var = f"{var}_OPERATOR_{type(self).__name__}"
        self.var = var
        self.to_select_var = concat_var
        return f"(GROUP_CONCAT({var}; separator='{separator}') AS {concat_var})"
class hasonly(has_filter):
    """
    Same filter as has(), but used for exclusive condition in query
    """
    def to_select(self, var, separator='###'):
        concat_var = f"{var}_OPERATOR_{type(self).__name__}"
        self.var = var
        self.to_select_var = concat_var
        return f"(GROUP_CONCAT({var}; separator='{separator}') AS {concat_var})"

class nothas(Operator):
    def to_sparql(self, var, val, owner='s'):
        clean_val = '(%s)' % ', '.join(map(str, val))
        return f"FILTER({var} NOT IN {clean_val})"

class exists(Operator):
    def to_sparql(self, var, val, owner='s'):
        v1 = generate_random_var()
        return f"FILTER EXISTS {{?{owner} {self.prop_str} ?{v1}}}"

class notexists(Operator):
    def to_sparql(self, var, val, owner='s'):
        v1 = generate_random_var()
        return f"FILTER NOT EXISTS {{?{owner} {self.prop_str} ?{v1}}}"
