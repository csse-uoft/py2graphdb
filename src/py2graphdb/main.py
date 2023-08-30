import unittest
from .utils.misc_lib import *
import os
from pprint import pprint
import re
import numpy as np

from owlready2 import default_world, onto_path, DataProperty, ObjectProperty, rdfs, Thing
onto_path.append('input/ontology_cache/')
from .config import config as CONFIG
if os.path.exists(CONFIG.LOG_FILE): os.remove(CONFIG.LOG_FILE)
CONFIG.STORE_LOCAL = False

utest = default_world.get_ontology(CONFIG.NM)
with utest:
    from .Models.graph_node import GraphNode

    class hasOneStr(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [str]

    class hasListOfURIs(ObjectProperty):
        rdfs.comment = ["Desc for the object"]
        range = [Thing]



import re
class SampleNode(GraphNode):
    """

        ...

        Attributes
        ----------
    """
    klass = 'utest.UnitTestNode1'
    relations = {
        'list_of_uris' : {'pred':utest.hasListOfURIs, 'cardinality':'many'},
        'one_str' : {'pred':utest.hasOneStr, 'cardinality':'one'},
    }

    def __init__(self, inst_id=None, keep_db_in_synch=False) -> None:
        super().__init__(inst_id=inst_id, keep_db_in_synch=keep_db_in_synch)

        
    from .utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, Thing
    imported_code = open('src/py2graphdb/utils/_model_getters_setters_deleters.py').read()
    exec(imported_code)

if __name__ == '__main__':
    with utest:
        node = SampleNode()
        print(node)