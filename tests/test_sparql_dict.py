import unittest
from src.utils.misc_lib import *
import os

from config import config as CONFIG

if os.path.exists(CONFIG.LOG_FILE): os.remove(CONFIG.LOG_FILE)

from owlready2 import default_world, onto_path, Thing
onto_path.append('input/ontology_cache/')

utest = default_world.get_ontology(CONFIG.NM)

CONFIG.STORE_LOCAL = False

from owlready2.prop import DataProperty, rdfs
with utest:
    class TestThing(Thing):
        pass

    class title(DataProperty):
        rdfs.comment = ["Title for the object"]
        range = [str]

    class desc(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [str]


with utest:
    from pprint import pprint
    import re
    import numpy as np
    from src.utils.db_utils import global_db
    from src.utils.db_utils import resolve_nm_for_ttl, SPARQLDict
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
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr})."})
            inst_id1 = inst['ID']

            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr})."})
            inst_id2 = inst['ID']
            self.assertEqual(inst_id1, inst_id2)

    def test_2(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr})."})
            inst_id1 = inst['ID']

            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr})."})
            inst_id2 = inst['ID']
            self.assertEqual(inst_id1, inst_id2)

    def test_3(self):
        with utest:
            rr1 = np.random.rand()
            rr2 = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr1})."})
            inst_id1 = inst['ID']

            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr2})."})
            inst_id2 = inst['ID']
            self.assertNotEqual(inst_id1, inst_id2)

    def test_4(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr})."})
            self.assertIsNone(inst)

    def test_5(self):
        with utest:
            rr = f"{int(np.random.rand()*10**10)}"
            inst = SPARQLDict._get(klass=utest.TestThing, inst_id = str(rr))
            self.assertIsNone(inst)

    def test_6(self):
        with utest:
            inst = SPARQLDict._add(klass=utest.TestThing)
            self.assertIn('ID', inst.keys())

    def test_7(self):
        with utest:
            rr = f"{int(np.random.rand()*10**10)}"
            inst = SPARQLDict._add(klass=utest.TestThing, inst_id = str(rr))
            self.assertEqual(inst['ID'], f"utest.{rr}")


    def test_8(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            rr2 = f"utest.{rr1}"
            rr3 = resolve_nm_for_ttl(rr2)
            self.assertEqual(f"utest:{rr1}", rr3)

    def test_9(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            rr2 = resolve_nm_for_ttl(rr1)
            self.assertEqual(f"utest:{rr1}", rr2)

    def test_10(self):
        with utest:
            rr = str(int(np.random.rand()*10**10))
            props = {utest.title:'my new title', utest.desc:f"My desc with {rr}"}
            inst_id = str(int(np.random.rand()*10**10))
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_get = SPARQLDict._get(klass=utest.TestThing, inst_id=inst_id)
            self.assertEqual(inst_add, inst_get)

    def test_11(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_get = SPARQLDict._get(klass=utest.TestThing, inst_id=inst_id)
            self.assertEqual(inst_add, inst_get)

    def test_12(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            updated_props = props.copy()
            updated_props[utest.title] = ['my new title 1']
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, drop=updated_props)
            self.assertEqual(inst_updated[utest.title], ['my title 2'])
            self.assertNotIn(utest.desc, inst_updated.keys())

    def test_13(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = inst_add['ID']
            inst_id = f"utest.{rr2}"
            updated_props = props.copy()
            updated_props = {utest.title: ['my title 3', 'my title 4']}
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, add=updated_props)
            self.assertEqual(4, len([t for t in inst_updated[utest.title] if t in ['my new title 1', 'my title 2', 'my title 3', 'my title 4']]))
            self.assertEqual(inst_updated[utest.desc], [f"My desc with {rr1}"])


    def test_14(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:None, utest.desc:f"this is my trace ({rr})."})
            inst_id = inst['ID']
            inst2 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id)
            self.assertNotIn(utest.title, inst2.keys())

    def test_15(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:None, utest.desc:f"this is my trace ({rr})."})
            inst_id = inst['ID']
            inst2 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id)
            self.assertIn('ID', inst2.keys())
            self.assertIn('is_a', inst2.keys())
            self.assertIn(utest.desc, inst2.keys())
            self.assertIn(utest.hasUUID, inst2.keys())
            self.assertEqual(len(inst2.keys()), 4)

    def test_16(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:["My title"], utest.desc:f"this is my trace ({rr})."})
            inst_id = inst['ID']

            inst2 = SPARQLDict._update(klass=utest.TestThing, inst_id=inst_id, drop={utest.title:["My title"]})
            self.assertIn('ID', inst2.keys())
            self.assertIn('is_a', inst2.keys())
            self.assertIn(utest.desc, inst2.keys())
            self.assertIn(utest.hasUUID, inst2.keys())
            self.assertEqual(len(inst2.keys()), 4)

    def test_17(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:["My title"], utest.desc:f"this is my trace ({rr})."})
            inst_id = inst['ID']
            new_props = {utest.title:['My NEW Title'], utest.desc:f"this is my NEW trace ({rr})."}
            inst2 = SPARQLDict._update(klass=utest.TestThing, inst_id=inst_id, add=new_props)
            self.assertIn('ID', inst2.keys())
            self.assertIn('is_a', inst2.keys())
            self.assertIn(utest.desc, inst2.keys())
            self.assertIn(utest.hasUUID, inst2.keys())
            self.assertIn(utest.title, inst2.keys())
            self.assertEqual(len(inst2.keys()), 5)
            self.assertEqual(len(inst2[utest.desc]), 2)
            self.assertEqual(len(inst2[utest.title]), 2)

    def test_18(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:["My title"], utest.desc:f"this is my trace ({rr})."})
            inst_id = inst['ID']
            new_props = {utest.title:['My NEW Title 1','My NEW Title 2' ], utest.desc:[f"this is my NEW trace ({rr}).", "A NEW desc #2"]}
            inst2 = SPARQLDict._update(klass=utest.TestThing, inst_id=inst_id, new=new_props)
            self.assertIn('ID', inst2.keys())
            self.assertIn('is_a', inst2.keys())
            self.assertIn(utest.desc, inst2.keys())
            self.assertIn(utest.hasUUID, inst2.keys())
            self.assertIn(utest.title, inst2.keys())
            self.assertEqual(len(inst2.keys()), 5)
            self.assertIn('My NEW Title 1', inst2[utest.title])
            self.assertIn('My NEW Title 2', inst2[utest.title])
            self.assertEqual(len(inst2[utest.title]), 2)
            self.assertIn("A NEW desc #2" in inst2[utest.desc] and f"this is my NEW trace ({rr}).", inst2[utest.desc])
            self.assertEqual(len(inst2[utest.desc]), 2)


if __name__ == '__main__':
    unittest.main(exit=False)
