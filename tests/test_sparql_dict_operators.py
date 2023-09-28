import unittest
from src.py2graphdb.utils.misc_lib import *
import os

from src.py2graphdb.config import config as CONFIG

if os.path.exists(CONFIG.LOG_FILE): os.remove(CONFIG.LOG_FILE)

from owlready2 import default_world, onto_path, Thing, DataProperty, ObjectProperty
onto_path.append('input/ontology_cache/')

utest = default_world.get_ontology(CONFIG.NM)

CONFIG.STORE_LOCAL = False

from owlready2.prop import rdfs
from src.py2graphdb.ontology.operators import *
# from src.py2graphdb.utils.db_utils import _resolve_nm, resolve_nm_for_ttl, resolve_nm_for_dict

with utest:
    class TestThing(Thing):
        pass

    class title(DataProperty):
        rdfs.comment = ["Title for the object"]
        range = [str]

    class desc(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [str]

    class hasint(DataProperty):
        rdfs.comment = ["Int for the object"]
        range = [int]

    class hasuri(ObjectProperty):
        rdfs.comment = ["URI for the object"]
        range = [Thing]

    class foruri(ObjectProperty):
        rdfs.comment = ["URI for the object"]
        range = [Thing]
        inverse_property = hasuri


    class hasUUID(DataProperty):
        rdfs.comment = ["UUID for the object, if applicable"]
        range = [str]

with utest:
    from pprint import pprint
    import re
    import numpy as np
    from src.py2graphdb.utils.db_utils import global_db
    from src.py2graphdb.utils.db_utils import resolve_nm_for_ttl, SPARQLDict
    print()

class TestSPARQLDict(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from graphdb_importer import import_and_wait, set_config
        TMP_DIR = './tmp/'
        _ = os.makedirs(TMP_DIR) if not os.path.exists(TMP_DIR) else None
        owl_file = f'{TMP_DIR}unit_test_sparql.owl'
        utest.save(owl_file)
        set_config(CONFIG.SERVER_URL, CONFIG.REPOSITORY, username='admin', password='admin')
        import_and_wait(owl_file, replace_graph=True)

        SPARQLDict._clear_graph(graph=CONFIG.GRAPH_NAME)


    def test_1(self):
        # eq operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={eq(utest.hasint):3, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 1)
            self.assertIn(inst3['ID'], inst_ids)
 
    def test_1_bool1(self):
        # eq operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={eq(utest.hasbool):True, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)
            self.assertEqual(len(insts), 2)
 
    def test_1_bool2(self):
        # eq operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={eq(utest.hasbool):False, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)
            self.assertEqual(len(insts), 2)
 
    def test_2(self):
        # ne operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={ne(utest.hasint):3, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 3)
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)
 

    def test_2_bool1(self):
        # ne operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={ne(utest.hasbool):True, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)
 
    def test_2_bool1(self):
        # ne operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={ne(utest.hasbool):False, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)
 

    def test_3(self):
        # le operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={le(utest.hasint):3, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 3)
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)
 
    def test_4(self):
        # ge operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={ge(utest.hasint):2, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 3)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)

    def test_5(self):
        # lt operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={lt(utest.hasint):3, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst2['ID'], inst_ids)
 
    def test_6(self):
        # gt operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={gt(utest.hasint):1, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 3)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)


    def test_7(self):
        # has operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={has(utest.hasint):[2,4], utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)

    def test_7_bool1(self):
        # has operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={has(utest.hasbool):[True], utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)

    def test_7_bool2(self):
        # has operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={has(utest.hasbool):[False], utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)

    def test_7_bool3(self):
        # has operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={has(utest.hasbool):[False, True], utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 4)
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)

    def test_8(self):
        # nothas operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={nothas(utest.hasint):[1,3], utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)

    def test_8_bool1(self):
        # nothas operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={nothas(utest.hasbool):[True], utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)

    def test_11(self):
        # eq operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={eq(utest.hasint):3, utest.desc:f"this is my trace ({rr})."}, how='first')
            self.assertEqual(insts[0]['ID'], inst3['ID'])
            self.assertEqual(len(insts), 1)
 
    def test_12(self):
        # ne operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={ne(utest.hasint):3, utest.desc:f"this is my trace ({rr})."}, how='first')
            self.assertEqual(insts[0]['ID'], inst1['ID'])
            self.assertEqual(len(insts), 1)

    def test_13(self):
        # le operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={le(utest.hasint):3, utest.desc:f"this is my trace ({rr})."}, how='first')
            self.assertEqual(insts[0]['ID'], inst1['ID'])
            self.assertEqual(len(insts), 1)
 
    def test_14(self):
        # ge operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={ge(utest.hasint):2, utest.desc:f"this is my trace ({rr})."}, how='first')
            self.assertEqual(insts[0]['ID'], inst2['ID'])
            self.assertEqual(len(insts), 1)

    def test_15(self):
        # lt operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={lt(utest.hasint):3, utest.desc:f"this is my trace ({rr})."}, how='first')
            self.assertEqual(insts[0]['ID'], inst1['ID'])
            self.assertEqual(len(insts), 1)
 
    def test_16(self):
        # gt operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={gt(utest.hasint):1, utest.desc:f"this is my trace ({rr})."}, how='first')
            self.assertEqual(insts[0]['ID'], inst2['ID'])
            self.assertEqual(len(insts), 1)
 
    def test_17(self):
        # has operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={has(utest.hasint):[2,4], utest.desc:f"this is my trace ({rr})."}, how='first')
            self.assertEqual(insts[0]['ID'], inst2['ID'])
            self.assertEqual(len(insts), 1)

    def test_18(self):
        # nothas operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:1, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:2, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={nothas(utest.hasint):[1,3], utest.desc:f"this is my trace ({rr})."}, how='first')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 1)
            self.assertIn(inst2['ID'], inst_ids)
            # self.assertIn(inst4['ID'], inst_ids)

    def test_20(self):
        # exists operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={exists(utest.hasint):None, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst3['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)

    def test_20_bool1(self):
        # exists operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={exists(utest.hasbool):None, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 4)
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)
            self.assertIn(inst4['ID'], inst_ids)

    def test_21(self):
        # not exists operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={notexists(utest.hasint):None, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 4)
            self.assertIn(inst1['ID'], inst_ids)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst5['ID'], inst_ids)
            self.assertIn(inst6['ID'], inst_ids)

    def test_21_bool1(self):
        # not exists operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:True, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={notexists(utest.hasbool):None, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst5['ID'], inst_ids)
            self.assertIn(inst6['ID'], inst_ids)

    def test_22(self):
        # exists operator with how='first'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={exists(utest.hasint):None, utest.desc:f"this is my trace ({rr})."}, how='first')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 1)
            self.assertIn(inst3['ID'], inst_ids)
            # self.assertIn(inst4['ID'], inst_ids)

    def test_23(self):
        # not exists operator with how='all'
        with utest:
            rr = np.random.rand()
            inst1 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:3, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, props={utest.hasint:4, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={notexists(utest.hasint):None, utest.desc:f"this is my trace ({rr})."}, how='first')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 1)
            self.assertIn(inst1['ID'], inst_ids)
            # self.assertIn(inst2['ID'], inst_ids)

    # TODO: add tests for string filter
    # TODO: add tests for combination of operators

if __name__ == '__main__':
    unittest.main(exit=False)
