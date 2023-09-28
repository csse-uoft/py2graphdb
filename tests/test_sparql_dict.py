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
from src.py2graphdb.utils.db_utils import _resolve_nm, resolve_nm_for_ttl, resolve_nm_for_dict

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

    class hasbool(DataProperty):
        rdfs.comment = ["Boolean for the object"]
        range = [bool]

    class hasfloat(DataProperty):
        rdfs.comment = ["Float for the object"]
        range = [float]

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

    def test_12_bool1(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasbool:[True]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, drop={utest.hasbool:True}, add={utest.hasbool:False})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertEqual(inst_updated[utest.hasbool], [False])
            self.assertEqual(inst_get[utest.hasbool], [False])

    def test_12_bool2(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasbool:[True]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, add={utest.hasbool:False})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertIn(True, inst_updated[utest.hasbool])
            self.assertIn(False, inst_updated[utest.hasbool])
            self.assertEqual(len(inst_updated[utest.hasbool]), 2)
            self.assertIn(True, inst_get[utest.hasbool])
            self.assertIn(False, inst_get[utest.hasbool])
            self.assertEqual(len(inst_get[utest.hasbool]), 2)


    def test_12_bool3(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasbool:[True]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, new={utest.hasbool:False})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertEqual(inst_updated[utest.hasbool], [False])
            self.assertEqual(inst_get[utest.hasbool], [False])

    def test_12_int1(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasint:[123]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, drop={utest.hasint:123}, add={utest.hasint:456})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertEqual(inst_updated[utest.hasint], [456])
            self.assertEqual(inst_get[utest.hasint], [456])

    def test_12_int2(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasint:[123]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, add={utest.hasint:456})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertIn(123, inst_updated[utest.hasint])
            self.assertIn(456, inst_updated[utest.hasint])
            self.assertEqual(len(inst_updated[utest.hasint]), 2)
            self.assertIn(123, inst_get[utest.hasint])
            self.assertIn(456, inst_get[utest.hasint])
            self.assertEqual(len(inst_get[utest.hasint]), 2)

    def test_12_int3(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasint:[123, 456]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, new={utest.hasint:789})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertEqual(inst_updated[utest.hasint], [789])
            self.assertEqual(inst_get[utest.hasint], [789])


    def test_12_float1(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasfloat:[0.123]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, drop={utest.hasfloat:0.123}, add={utest.hasfloat:0.456})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertEqual(inst_updated[utest.hasfloat], [0.456])
            self.assertEqual(inst_get[utest.hasfloat], [0.456])

    def test_12_float2(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasfloat:[0.123]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, add={utest.hasfloat:0.456})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertIn(0.123, inst_updated[utest.hasfloat])
            self.assertIn(0.456, inst_updated[utest.hasfloat])
            self.assertEqual(len(inst_updated[utest.hasfloat]), 2)
            self.assertIn(0.123, inst_get[utest.hasfloat])
            self.assertIn(0.456, inst_get[utest.hasfloat])
            self.assertEqual(len(inst_get[utest.hasfloat]), 2)

    def test_12_float3(self):
        with utest:
            rr1 = str(int(np.random.rand()*10**10))
            props = {utest.title:['my new title 1', 'my title 2'], utest.desc:[f"My desc with {rr1}"], utest.hasfloat:[0.123]}
            rr2 = str(int(np.random.rand()*10**10))
            inst_id = rr2
            inst_add = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id, props=props)
            inst_id = f"utest.{rr2}"
            inst_updated = SPARQLDict._update(klass=utest.TestThing,inst_id=inst_id, new={utest.hasfloat:0.456})
            inst_get = SPARQLDict._get(klass=utest.TestThing,inst_id=inst_id)
            self.assertEqual(inst_updated[utest.hasfloat], [0.456])
            self.assertEqual(inst_get[utest.hasfloat], [0.456])


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

    def test_19(self):
        # test _get() without klass, only inst_id
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:["My title"], utest.desc:f"this is my trace ({rr})."})
            inst_id = inst['ID']
            inst2 = SPARQLDict._get(inst_id=inst_id)
            self.assertIn('ID', inst2.keys())
            self.assertIn('is_a', inst2.keys())
            self.assertIn(utest.desc, inst2.keys())
            self.assertIn(utest.hasUUID, inst2.keys())
            self.assertIn(utest.title, inst2.keys())
            self.assertEqual(inst2['ID'], inst_id)
            self.assertEqual(inst2[utest.desc], [f"this is my trace ({rr})."])
            self.assertEqual(inst['is_a'], utest.TestThing)

    def test_20(self):
        # test _update() without klass, only inst_id and new properties
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:["My title"], utest.desc:f"this is my trace ({rr})."})
            inst_id = inst['ID']
            new_props = {utest.title:['My NEW Title 1','My NEW Title 2' ], utest.desc:[f"this is my NEW trace ({rr}).", "A NEW desc #2"]}
            inst2 = SPARQLDict._update(inst_id=inst_id, new=new_props)
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


    def test_32(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasint:1})
            inst_id1 = inst['ID']

            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasint:1})
            inst_id2 = inst['ID']
            self.assertEqual(inst_id1, inst_id2)

    def test_33(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasint:11})
            inst_id1 = inst['ID']

            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasint:12})
            self.assertIsNone(inst)

    def test_34(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasfloat:rr})
            inst_id1 = inst['ID']

            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasfloat:rr})
            inst_id2 = inst['ID']
            self.assertEqual(inst_id1, inst_id2)

    def test_35(self):
        with utest:
            rr0 = np.random.rand()
            rr1 = np.random.rand()
            rr2 = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr0}).", utest.hasfloat:rr1})
            inst_id1 = inst['ID']

            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr0}).", utest.hasfloat:rr2})
            self.assertIsNone(inst)


    def test_36(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:False})
            inst_id1 = inst['ID']

            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:False})
            inst_id2 = inst['ID']
            self.assertEqual(inst_id1, inst_id2)

    def test_37(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:True})
            inst_id1 = inst['ID']

            inst = SPARQLDict._get(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:True})
            inst_id2 = inst['ID']
            self.assertEqual(inst_id1, inst_id2)


    def test_36(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:True})
            inst_id1 = inst['ID']
            self.assertEqual(len(inst[utest.hasbool]), 1)
            self.assertIn(True,inst[utest.hasbool])

    def test_37(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:False})
            self.assertEqual(len(inst[utest.hasbool]), 1)
            self.assertIn(False,inst[utest.hasbool])

    def test_38(self):
        with utest:
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False})
            inst_id1 = inst['ID']

            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.hasbool:False})
            inst_id2 = inst['ID']
            self.assertNotEqual(inst_id1, inst_id2)

    def test_39(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:False})
            inst_id1 = inst['ID']

            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:False})
            inst_id2 = inst['ID']
            self.assertNotEqual(inst_id1, inst_id2)


    def test_40(self):
        # search with uri property
        with utest:
            rr = np.random.rand()
            rr1 = str(int(np.random.rand()*10**10))
            inst_id1 = f"utest.{rr1}"
            rr2 = str(int(np.random.rand()*10**10))
            inst_id2 = f"utest.{rr2}"
            rr3 = str(int(np.random.rand()*10**10))
            inst_id3 = f"utest.{rr3}"
            rr4 = str(int(np.random.rand()*10**10))
            inst_id4 = f"utest.{rr4}"
            rr5 = str(int(np.random.rand()*10**10))
            inst_id5 = f"utest.{rr5}"
            rr6 = str(int(np.random.rand()*10**10))
            inst_id6 = f"utest.{rr6}"
            inst1 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id1, props={utest.hasuri:inst_id6, utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
            inst2 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id2,  props={utest.hasuri:inst_id1, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
            inst3 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id3,  props={utest.hasuri:inst_id1, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
            inst4 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id4,  props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst5 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id5,  props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
            inst6 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id6,  props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

            insts = SPARQLDict._search(klass=utest.TestThing, props={utest.hasuri:inst_id1, utest.desc:f"this is my trace ({rr})."}, how='all')
            inst_ids = [inst['ID'] for inst in insts]
            self.assertEqual(len(insts), 2)
            self.assertIn(inst2['ID'], inst_ids)
            self.assertIn(inst3['ID'], inst_ids)

    # def test_41(self):
    #     # search with uri with inverse property
    #     with utest:
    #         rr = np.random.rand()
    #         rr1 = str(int(np.random.rand()*10**10))
    #         inst_id1 = f"utest.{rr1}"
    #         rr2 = str(int(np.random.rand()*10**10))
    #         inst_id2 = f"utest.{rr2}"
    #         rr3 = str(int(np.random.rand()*10**10))
    #         inst_id3 = f"utest.{rr3}"
    #         rr4 = str(int(np.random.rand()*10**10))
    #         inst_id4 = f"utest.{rr4}"
    #         rr5 = str(int(np.random.rand()*10**10))
    #         inst_id5 = f"utest.{rr5}"
    #         rr6 = str(int(np.random.rand()*10**10))
    #         inst_id6 = f"utest.{rr6}"
    #         inst1 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id1, props={utest.title:'My TestThing 1', utest.desc:f"this is my trace ({rr})."})
    #         inst2 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id2,  props={utest.hasuri:inst_id1, utest.title:'My TestThing 2', utest.desc:f"this is my trace ({rr})."})
    #         inst3 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id3,  props={utest.hasuri:inst_id1, utest.title:'My TestThing 3', utest.desc:f"this is my trace ({rr})."})
    #         inst4 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id4,  props={utest.hasuri:inst_id2, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
    #         inst5 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id5,  props={utest.hasuri:inst_id2, utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})
    #         inst6 = SPARQLDict._add(klass=utest.TestThing, inst_id=inst_id6,  props={utest.title:'My TestThing 4', utest.desc:f"this is my trace ({rr})."})

    #         insts = SPARQLDict._search(klass=utest.TestThing, props={utest.foruri:inst_id2, utest.desc:f"this is my trace ({rr})."}, how='all')
    #         inst_ids = [inst['ID'] for inst in insts]
    #         self.assertEqual(len(insts), 1)
    #         self.assertIn(inst1['ID'], inst_ids)

    def test_50(self):
        with utest:
            rr = np.random.rand()
            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:True})
            inst_id1 = inst['ID']

            inst = SPARQLDict._add(klass=utest.TestThing, props={utest.title:'My TestThing', utest.desc:f"this is my trace ({rr}).", utest.hasbool:True})
            inst_id2 = inst['ID']
            self.assertNotEqual(inst_id1, inst_id2)



    def test_51(self):
        with utest:
            # mimic resolve_nm_for_ttl
            res = _resolve_nm(utest.TestThing, from_delimiter='.', to_delimiter=':')
            self.assertEqual(res, 'utest:TestThing')

    def test_52(self):
        with utest:
            # mimic resolve_nm_for_ttl
            res = _resolve_nm('.TestThing', from_delimiter='.', to_delimiter=':')
            self.assertEqual(res, 'utest:TestThing')

    def test_53(self):
        with utest:
            # mimic resolve_nm_for_ttl
            res = _resolve_nm('utest:TestThing', from_delimiter='.', to_delimiter=':')
            self.assertEqual(res, 'utest:TestThing')

    def test_54(self):
        with utest:
            # mimic resolve_nm_for_ttl
            res = _resolve_nm(':TestThing', from_delimiter='.', to_delimiter=':')
            self.assertEqual(res, 'utest:TestThing')

    def test_60(self):
        with utest:
            # mimic resolve_nm_for_dict
            res = _resolve_nm(utest.TestThing, from_delimiter=':', to_delimiter='.')
            self.assertEqual(res, 'utest.TestThing')

    def test_61(self):
        with utest:
            # mimic resolve_nm_for_dict
            res = _resolve_nm('.TestThing', from_delimiter=':', to_delimiter='.')
            self.assertEqual(res, 'utest.TestThing')

    def test_62(self):
        with utest:
            # mimic resolve_nm_for_dict
            res = _resolve_nm('utest:TestThing', from_delimiter=':', to_delimiter='.')
            self.assertEqual(res, 'utest.TestThing')

    def test_63(self):
        with utest:
            # mimic resolve_nm_for_dict
            res = _resolve_nm(':TestThing', from_delimiter=':', to_delimiter='.')
            self.assertEqual(res, 'utest.TestThing')


    def test_70(self):
        # resolve_nm_for_ttl
        with utest:
            res = resolve_nm_for_ttl(utest.TestThing)
            self.assertEqual(res, 'utest:TestThing')

    def test_71(self):
        # resolve_nm_for_ttl
        with utest:
            res = resolve_nm_for_ttl('.TestThing')
            self.assertEqual(res, 'utest:TestThing')

    def test_72(self):
        # resolve_nm_for_ttl
        with utest:
            res = resolve_nm_for_ttl('utest:TestThing')
            self.assertEqual(res, 'utest:TestThing')

    def test_73(self):
        # resolve_nm_for_ttl
        with utest:
            res = resolve_nm_for_ttl(':TestThing')
            self.assertEqual(res, 'utest:TestThing')

    def test_80(self):
        # resolve_nm_for_dict
        with utest:
            res = resolve_nm_for_dict(utest.TestThing)
            self.assertEqual(res, 'utest.TestThing')

    def test_81(self):
        # resolve_nm_for_dict
        with utest:
            res = resolve_nm_for_dict('.TestThing')
            self.assertEqual(res, 'utest.TestThing')

    def test_82(self):
        # resolve_nm_for_dict
        with utest:
            res = resolve_nm_for_dict('utest:TestThing')
            self.assertEqual(res, 'utest.TestThing')

    def test_83(self):
        # resolve_nm_for_dict
        with utest:
            res = resolve_nm_for_dict(':TestThing')
            self.assertEqual(res, 'utest.TestThing')


if __name__ == '__main__':
    unittest.main(exit=False)
