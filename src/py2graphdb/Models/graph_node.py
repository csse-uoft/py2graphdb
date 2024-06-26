from ..utils.db_utils import SPARQLDict, PropertyList,get_instance_label, resolve_nm_for_ttl, resolve_nm_for_dict, Thing, ThingClass, _resolve_nm, default_world
import re, hashlib, os
from ..config import config as CONFIG
from datetime import datetime
exec(f"{CONFIG.PREFIX} = default_world.get_namespace(\"{CONFIG.NM}\")")

class GraphNode(Thing):
    """
    A db Model class that defines the schema for the Text data level.
    Base schema is extended from the Hypothesis class.

    ...

    Attributes
    ----------
    __tablename__ : str
        The name of the database table
    content : SQLAlchemy.Column
        String value of this term

    """
    klass = f'{CONFIG.PREFIX}.GraphNode'
    inst_id = None
    relations = {}
    created_at = None
    keep_db_in_synch = False
    graph_is_a = None
    def __init__(self, inst_id=None, inst=None, keep_db_in_synch=False) -> None:
        created_at = datetime.now()
        super().__init__()

        self.keep_db_in_synch = keep_db_in_synch

        if inst_id: self.inst_id = resolve_nm_for_dict(str(inst_id))
        self.load(inst=inst)
        if not self.inst_id: self.inst_id = get_instance_label(klass = self.klass)
        
    @property
    def id(self):
        return self.inst_id


    from ..utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, Thing, resolve_nm_for_dict
    from ..utils import db_utils
    def_file_path = os.path.dirname(db_utils.__file__) + '/_model_getters_setters_deleters.py'
    imported_code = open(def_file_path).read()
    exec(imported_code)

    def __repr__(self):
        return str(self.inst_id) or ''

    def key(self):
        s = self.key_show()
        return int(hashlib.sha256(s.encode('utf-8')).hexdigest(), 16) % 10**8
       
    def key_show(self):
        return f"{self.__class__.__name__}_{self.inst_id}"

    def drop(self, val, value=None):
        if val in [re.sub('^_','',d) for d in self.__dir__() if re.match(r'_[^_].+$', d) and d not in ['_delete', '_add', '_get', '_update']]:
            props = self.relations[val]
            pred = props['pred']
            cardinality = props['cardinality']
            kind = pred.range[0]


            if value is None:
                # deleting all values
                value_to_delete = eval(f"self._{val}")
                if cardinality!='many':
                    exec(f"self._{val} = None")
                else:
                    exec(f"self._{val} = []")


            else:
                value_to_delete = value
                if cardinality!='many':
                    exec(f"self._{val} = None")
                else:
                    if isinstance(value, (PropertyList,list)):
                        for v in value:
                            exec(f'self._{val}.remove(v)')
                    else:
                        exec(f"self._{val}.remove(value)")

            if self.keep_db_in_synch:
                pred = self.relations[val]['pred']
                SPARQLDict._update(klass=self.klass,inst_id=self.inst_id, drop={pred:value_to_delete})
        else:
            raise(ValueError(f"Can't drop value(s). {val} is not a valid property for {self.__class__.__name__}"))
        return


    def cast_to_graph_type(self):
        if self.graph_is_a:
            if isinstance(self.graph_is_a, str):
                tmp = _resolve_nm(default_world.get_namespace(self.graph_is_a).name, from_delimiter='#',to_delimiter='.')
                self.graph_is_a = eval(tmp)

            return self.graph_is_a(self)
        else:
            return self


    @classmethod
    def find(cls, inst_id):
        """Find an existing text query with the given parameters and return it.

        :return: found/generated text query
        """
        inst = SPARQLDict._get(inst_id=inst_id)
        if inst is not None:
            return cls(inst=inst) if inst else None
        else:
            return

    @classmethod
    def generate(cls, inst_id=None):
        #     """Generate a new text query with the given parameters and return it.

        #     :param inst_id: the trace id for this text
        #     :return: found/generated text query
        inst = SPARQLDict._add(klass=cls.klass,inst_id=inst_id)
        if inst is not None:
            return cls(inst=inst) if inst else None
        else:
            return

    @classmethod
    def find_generate(cls, inst_id):
        """Try to find and return an existing Node query with the given parameters.
            If there is none, generate a new query and return it.

        :param inst_id: id of instance in the knowledge graph
        :return: found/generated dep query
        """
        node = cls.find(inst_id=inst_id)
        if node is None:
            node = cls.generate(inst_id=inst_id)
        return node