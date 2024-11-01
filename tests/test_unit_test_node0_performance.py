import unittest
from src.py2graphdb.utils.misc_lib import *
import os
from pprint import pprint
import re
import numpy as np
import tqdm
from owlready2 import default_world, onto_path, ObjectProperty, DataProperty, rdfs, Thing

onto_path.append('input/ontology_cache/')
from src.py2graphdb.config import config as CONFIG
if os.path.exists(CONFIG.LOG_FILE):
  os.remove(CONFIG.LOG_FILE)
CONFIG.STORE_LOCAL = False

utest = default_world.get_ontology(CONFIG.NM)
from src.py2graphdb.ontology.operators import *
with utest:
    from src.py2graphdb.Models.graph_node import GraphNode
    from src.py2graphdb.utils.db_utils import SPARQLDict, PropertyList
    print()

with utest:
    class hasOneIDStr(DataProperty):
        rdfs.comment = ["ID for the object"]
        range = [str]
    class hasManyStrs(DataProperty):
        rdfs.comment = ["Many strings for the object"]
        range = [str]
    class hasOneIntA(DataProperty):
        rdfs.comment = ["Int A for the object"]
        range = [int]
    class hasOneIntB(DataProperty):
        rdfs.comment = ["Int B for the object"]
        range = [int]



class UnitTestNode0(GraphNode):
    """

        ...

        Attributes
        ----------
    """
    klass = 'utest.UnitTestNode0'
    relations = {
        'id_str' : {'pred':utest.hasOneIDStr, 'cardinality':'one'},
        'many_strs' : {'pred':utest.hasManyStrs, 'cardinality':'many'},
        'int_a' : {'pred':utest.hasOneIntA, 'cardinality':'one'},
        'int_b' : {'pred':utest.hasOneIntB, 'cardinality':'one'},
    }

    def __init__(self, inst_id=None, inst=None, keep_db_in_synch=False) -> None:
        super().__init__(inst_id=inst_id, inst=inst, keep_db_in_synch=keep_db_in_synch)

        
    # from src.py2graphdb.utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, Thing
    imported_code = open('./src/py2graphdb/utils/_model_getters_setters_deleters.py').read()
    exec(imported_code)


    @classmethod
    def find(cls,  id_str, many_strs, int_a, int_b):
        inst =  SPARQLDict._get(klass=cls.klass, props={
            utest.hasOneIDStr   : id_str,
            utest.hasManyStrs   : many_strs,
            utest.hasOneIntA    : int_a,
            utest.hasOneIntB    : int_b
        })
        return cls(inst=inst) if inst else None

    @classmethod
    def generate(cls, id_str, many_strs, int_a, int_b):
        inst =  SPARQLDict._add(klass=cls.klass, props={
            utest.hasOneIDStr   : id_str,
            utest.hasManyStrs   : many_strs,
            utest.hasOneIntA    : int_a,
            utest.hasOneIntB    : int_b
        })

        return cls(inst=inst) if inst else None

    @classmethod
    def find_generate(cls, id_str=None, many_strs=None, int_a=None, int_b=None):
        """Try to find and return an existing phrase query with the given parameters.
        If there is none, generate a new query and return it.

        :param request_id: the trace id for this phrase
        :param content: the lexicon value for this phrase
        :param start: start position of phrase in the Text, starting at 0
        :param end: end position of phrase in the Text, starting at 0
        :param certainty: certainty level in float
        :return: found/generated phrase query
        """
        node = cls.find(id_str=id_str, many_strs=many_strs, int_a=int_a, int_b=int_b)
        if node is None:
            node = cls.generate(id_str=id_str, many_strs=many_strs, int_a=int_a, int_b=int_b)
        return node

class TestUnitTestNode0(unittest.TestCase):
    INIT_ITERS_N = 0
    ITERS_N = 100
    @classmethod
    def setUpClass(cls):
        from graphdb_importer import import_and_wait, set_config
        TMP_DIR = './tmp/'
        _ = os.makedirs(TMP_DIR) if not os.path.exists(TMP_DIR) else None
        owl_file = f'{TMP_DIR}unit_test_node0.owl'
        utest.save(owl_file)
        set_config(CONFIG.SERVER_URL, CONFIG.REPOSITORY, username='admin', password='admin')
        import_and_wait(owl_file, replace_graph=True)

        SPARQLDict._clear_graph(graph=CONFIG.GRAPH_NAME)

        for i in tqdm.tqdm(range(cls.INIT_ITERS_N)):
            _ = UnitTestNode0.generate(
                id_str = str(int(np.random.rand()*10**10)),
                many_strs = [str(int(np.random.rand()*10**10)) for i in range(10)],
                int_a = int(np.random.rand()*10),
                int_b = int(np.random.rand()*10)
            )

    def test_find(self):
        for i in tqdm.tqdm(range(self.ITERS_N), desc='find'):
            _ = UnitTestNode0.find(
                id_str = str(int(np.random.rand()*10**10)),
                many_strs = [str(int(np.random.rand()*10**10)) for i in range(10)],
                int_a = int(np.random.rand()*10),
                int_b = int(np.random.rand()*10)
            )


    def test_generate_find(self):
        with utest:
            for i in tqdm.tqdm(range(self.ITERS_N), desc='generate_find'):
                inst_1 = UnitTestNode0.generate(
                    id_str = str(int(np.random.rand()*10**10)),
                    many_strs = [str(int(np.random.rand()*10**10)) for i in range(10)],
                    int_a = int(np.random.rand()*10),
                    int_b = int(np.random.rand()*10)
                )

                inst_2 = UnitTestNode0.find(
                    id_str = inst_1.id_str,
                    many_strs = inst_1.many_strs,
                    int_a = inst_1.int_a,
                    int_b = inst_1.int_b
                )

    def test_generate_find_generate(self):
        with utest:
            for i in tqdm.tqdm(range(self.ITERS_N), desc='generate_find_generate'):
                inst_1 = UnitTestNode0.generate(
                    id_str = str(int(np.random.rand()*10**10)),
                    many_strs = [str(int(np.random.rand()*10**10)) for i in range(10)],
                    int_a = int(np.random.rand()*10),
                    int_b = int(np.random.rand()*10)
                )

                inst_2 = UnitTestNode0.find_generate(
                    id_str = inst_1.id_str,
                    many_strs = inst_1.many_strs,
                    int_a = inst_1.int_a,
                    int_b = inst_1.int_b
                )

    def test_generate_find_generate_on_id_str(self):
        with utest:
            for i in tqdm.tqdm(range(self.ITERS_N), desc='generate_find_generate_on_id_str'):
                inst_1 = UnitTestNode0.generate(
                    id_str = str(int(np.random.rand()*10**10)),
                    many_strs = [str(int(np.random.rand()*10**10)) for i in range(10)],
                    int_a = int(np.random.rand()*10),
                    int_b = int(np.random.rand()*10)
                )

                inst_2 = UnitTestNode0.find_generate(
                    id_str = inst_1.id_str
                )
    def test_save(self):
        with utest:
            for i in tqdm.tqdm(range(self.ITERS_N), desc='save'):
                inst_1 = UnitTestNode0.generate(
                    id_str = str(int(np.random.rand()*10**10)),
                    many_strs = [str(int(np.random.rand()*10**10)) for i in range(10)],
                    int_a = int(np.random.rand()*10),
                    int_b = int(np.random.rand()*10)
                )

                inst_1.keep_db_synch = False
                inst_1.many_strs = [str(int(np.random.rand()*10**10)) for i in range(10)],
                inst_1.int_a = int(np.random.rand()*10)
                inst_1.int_b = int(np.random.rand()*10)
                inst_1.save()

if __name__ == '__main__':
    unittest.main(exit=False)

