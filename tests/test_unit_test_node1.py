import unittest
from src.py2graphdb.utils.misc_lib import *
import os
from pprint import pprint
import re
import numpy as np

from owlready2 import default_world, onto_path
onto_path.append('input/ontology_cache/')
from src.py2graphdb.config import config as CONFIG
if os.path.exists(CONFIG.LOG_FILE): os.remove(CONFIG.LOG_FILE)
CONFIG.STORE_LOCAL = False

utest = default_world.get_ontology(CONFIG.NM)
with utest:
    from src.py2graphdb.utils.db_utils import SPARQLDict
    from tests.unit_test_ks import UnitTestNode1
    print()

class TestUnitTestNode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from graphdb_importer import import_and_wait, set_config
        TMP_DIR = './tmp/'
        _ = os.makedirs(TMP_DIR) if not os.path.exists(TMP_DIR) else None
        owl_file = f'{TMP_DIR}unit_test_node1.owl'
        utest.save(owl_file)
        set_config(CONFIG.SERVER_URL, CONFIG.REPOSITORY, username='admin', password='admin')
        import_and_wait(owl_file, replace_graph=True)

        SPARQLDict._clear_graph(graph=CONFIG.GRAPH_NAME)

    def test_1(self):
        with utest:
            # test GraphNode.inst_id setting
            rr = str(int(np.random.rand()*10**10))
            test_inst0 = UnitTestNode1(inst_id=rr)
            self.assertEqual(test_inst0.inst_id, f"utest.{rr}")

    def test_2(self):
        with utest:
            # test GraphNode.inst_id setting
            rr = int(np.random.rand()*10**10)
            test_inst0 = UnitTestNode1(inst_id=rr)
            self.assertEqual(test_inst0.inst_id, f"utest.{rr}")


    def test_3(self):
        with utest:
            # test GraphNode.inst_id setting
            rr = f"utest.{int(np.random.rand()*10**10)}"
            test_inst0 = UnitTestNode1(inst_id=rr)
            self.assertEqual(test_inst0.inst_id, rr)

    def test_4(self):
        with utest:
            # test GraphNode.inst_id setting
            rr = int(np.random.rand()*10**10)
            rr1 = f"utest:{rr}"
            test_inst0 = UnitTestNode1(inst_id=rr)
            self.assertEqual(test_inst0.inst_id, f"utest.{rr}")


    def test_5(self):
        with utest:
            # test GraphNode.inst_id setting
            rr = int(np.random.rand()*10**10)
            rr1 = f"rdfs:{rr}"
            test_inst0 = UnitTestNode1(inst_id=rr1)
            self.assertEqual(test_inst0.inst_id, f"rdfs.{rr}")


    def test_6(self):
        with utest:
            # test GraphNode.inst_id setting with invlaiud namespace
            rr = f"any_namespace:{int(np.random.rand()*10**10)}"
            with self.assertRaises(ValueError):
                UnitTestNode1(inst_id=rr)

    def test_7(self):
        with utest:
            # test GraphNode.find_generate on existing
            test_inst0 = UnitTestNode1()
            test_inst0.list_of_ints = 678
            test_inst0.list_of_ints = '456'
            self.assertEqual(test_inst0._list_of_ints, [678, 456])


    def test_8(self):
        with utest:
            # test GraphNode.find_generate on existing
            test_inst0 = UnitTestNode1()
            test_inst0.list_of_floats = 0.678
            test_inst0.list_of_floats = '0.456'
            self.assertEqual(test_inst0._list_of_floats, [0.678, 0.456])


    def test_9(self):
        with utest:
            test_inst1 = UnitTestNode1()
            self.assertEqual(test_inst1.list_of_ints, [])
            self.assertEqual(test_inst1.list_of_floats, [])
            self.assertEqual(test_inst1.list_of_strs, [])
            self.assertEqual(test_inst1.list_of_uris, [])
            self.assertEqual(test_inst1.one_int, None)
            self.assertEqual(test_inst1.one_str, None)
            self.assertEqual(test_inst1.one_uri, None)

    def test_10(self):
        with utest:
            test_inst2 = UnitTestNode1()
            test_inst2.list_of_strs = 112233
            test_inst2.list_of_strs = '445566'
            self.assertEqual(test_inst2.list_of_strs, ['112233','445566'])

    def test_11(self):
        with utest:
            test_inst2 = UnitTestNode1()
            test_inst2.list_of_strs = '778899'
            test_inst2.list_of_strs = '101012121313'
            self.assertEqual(test_inst2.list_of_strs, ['778899','101012121313'])
            test_inst2.list_of_strs = '141415151616'
            self.assertEqual(test_inst2.list_of_strs, ['778899','101012121313', '141415151616'])
            test_inst2.drop('list_of_strs', '101012121313')
            self.assertEqual(test_inst2.list_of_strs, ['778899', '141415151616'])

    def test_12(self):
        with utest:
            test_inst2 = UnitTestNode1()
            test_inst2.list_of_strs = '7788991010'
            test_inst2.list_of_strs = '1010121213131414'
            test_inst2.list_of_strs = '141415151616'
            test_inst2.drop('list_of_strs', '1010121213131414')
            test_inst2.list_of_strs = '202021212222'
            test_inst2.list_of_strs = '232324242525'

            self.assertEqual(test_inst2.list_of_strs, ['7788991010', '141415151616', '202021212222', '232324242525'])

            test_inst2.drop('list_of_strs', ['141415151616', '202021212222'])
            self.assertEqual(test_inst2.list_of_strs, ['7788991010', '232324242525'])


    def test_13(self):
        with utest:
            test_inst3 = UnitTestNode1()
            test_inst3.list_of_uris = 'rdfs.should_be_anything'
            test_inst3.list_of_uris = 'utest:anything_at_all'
            test_inst3.list_of_uris = 'utest.additional_things'
            self.assertEqual(len(test_inst3.list_of_uris), 3)
            self.assertIn('rdfs.should_be_anything', test_inst3.list_of_uris)
            self.assertIn('utest.anything_at_all', test_inst3.list_of_uris)
            self.assertIn('utest.additional_things', test_inst3.list_of_uris)
            # test_inst3.load()

    def test_14(self):
        with utest:
            test_inst4 = UnitTestNode1(inst_id='utest:byebye_12345678')
            test_inst4.one_uri = 'rdfs:should_be_anything'
            test_inst4.one_uri = 'utest.anything_at_all'
            self.assertEqual(test_inst4.one_uri, 'utest.anything_at_all')


    def test_15(self):
        with utest:
            test_inst5 = UnitTestNode1()
            test_inst5.one_uri = 'utest.anything_at_all'
            test_inst5.one_uri = 'rdfs:should_be_anything'
            self.assertEqual(test_inst5.one_uri, 'rdfs.should_be_anything')

    def test_16(self):
        with utest:
            test_inst5 = UnitTestNode1()
            test_inst5.one_uri = 'rdfs:should_be_anything'
            self.assertEqual(test_inst5.one_uri, 'rdfs.should_be_anything')

    def test_17(self):
        with utest:
            test_inst6 = UnitTestNode1()
            test_inst6.one_str = 'sample text here'
            self.assertEqual(test_inst6.one_str, 'sample text here')
            
    def test_18(self):
        with utest:
            test_inst6 = UnitTestNode1()
            test_inst6.one_str = 'sample text here'
            test_inst6.one_str = 'a new sample goeas here'
            self.assertEqual(test_inst6.one_str, 'a new sample goeas here')


    def test_19(self):
        with utest:
            test_inst7 = UnitTestNode1()
            test_inst7.one_int = 789
            self.assertEqual(test_inst7.one_int, 789)
            
    def test_20(self):
        with utest:
            test_inst8 = UnitTestNode1()
            test_inst8.one_int = 101112
            test_inst8.one_int = 131415
            self.assertEqual(test_inst8.one_int, 131415)

    def test_21(self):
        with utest:
            test_inst7 = UnitTestNode1()
            test_inst7.one_float = 0.789
            self.assertEqual(test_inst7.one_float, 0.789)
            
    def test_22(self):
        with utest:
            test_inst8 = UnitTestNode1()
            test_inst8.one_float = 0.101112
            test_inst8.one_float = 0.131415
            self.assertEqual(test_inst8.one_float, 0.131415)

    def test_23(self):
        with utest:
            inst_id = f"utest.{int(np.random.rand()*10**10)}"
            test_inst9 = UnitTestNode1(inst_id=inst_id)
            self.assertEqual(test_inst9.inst_id, inst_id)
            self.assertEqual(test_inst9.list_of_ints, [])
            self.assertEqual(test_inst9.list_of_floats, [])
            self.assertEqual(test_inst9.list_of_strs, [])
            self.assertEqual(test_inst9.list_of_uris, [])
            self.assertEqual(test_inst9.one_int, None)
            self.assertEqual(test_inst9.one_str, None)
            self.assertEqual(test_inst9.one_uri, None)

    def test_24(self):
        with utest:
            inst_id = f"utest.{int(np.random.rand()*10**10)}"
            test_inst10 = UnitTestNode1(inst_id=inst_id)
            test_inst10.one_int = 11987654
            test_inst10.one_float = 0.987456
            test_inst10.one_str = 'my name'
            self.assertEqual(test_inst10.one_int, 11987654)
            self.assertEqual(test_inst10.one_float, 0.987456)
            self.assertEqual(test_inst10.one_str, 'my name')

    def test_25(self):
        with utest:
            # test load_from_inst
            inst_id = f"utest.{int(np.random.rand()*10**10)}"
            test_inst10 = UnitTestNode1(inst_id=inst_id)
            test_inst10.keep_db_in_synch = True
            test_inst10.one_int = 11987654
            test_inst10.one_float = 0.987456
            test_inst10.one_str = 'my name'
            test_inst10.list_of_uris = 'utest.test1'
            test_inst10.list_of_uris = 'utest.test2'
            self.assertEqual(test_inst10.one_int, 11987654)
            self.assertEqual(test_inst10.one_float, 0.987456)
            self.assertEqual(test_inst10.one_str, 'my name')
            self.assertIn('utest.test1', test_inst10.list_of_uris)
            self.assertIn('utest.test2', test_inst10.list_of_uris)

            test_inst10_dict = SPARQLDict._get(klass='utest.UnitTestNode1', inst_id=inst_id)
            test_inst10_obj = UnitTestNode1.load_from_inst(inst=test_inst10_dict)
            self.assertEqual(test_inst10_obj.inst_id, inst_id)
            self.assertEqual(test_inst10_obj.one_int, 11987654)
            self.assertEqual(test_inst10.one_float, 0.987456)
            self.assertEqual(test_inst10.one_str, 'my name')



    def test_26(self):
        with utest:
            # test non-consistent update to DB with keep_db_in_synch=False
            test_inst2 = UnitTestNode1()
            test_inst2.keep_db_in_synch = False
            test_inst2.list_of_strs = '778899'
            test_inst2.list_of_strs = '232324242525'

            inst = SPARQLDict._get(klass=test_inst2.klass, inst_id=test_inst2.inst_id)
            self.assertIsNone(inst)

    def test_27(self):
        with utest:
            # test consistent update to DB with keep_db_in_synch=True
            test_inst2 = UnitTestNode1()
            test_inst2.keep_db_in_synch = True
            test_inst2.list_of_strs = 'abc 778899'
            test_inst2.list_of_strs = 'def 232324242525'

            inst = SPARQLDict._get(klass=test_inst2.klass, inst_id=test_inst2.inst_id)
            self.assertIn('abc 778899' in inst[utest.hasListOfStrs] and 'def 232324242525', inst[utest.hasListOfStrs])
            self.assertEqual(len(inst[utest.hasListOfStrs]), 2)

    def test_28(self):
        with utest:
            # test consistent update to DB with keep_db_in_synch=True
            test_inst2 = UnitTestNode1()
            test_inst2.list_of_strs = 'abc 778899'
            test_inst2.keep_db_in_synch = True
            test_inst2.list_of_strs = 'def 232324242525'
            test_inst2.list_of_strs = 'ghi 11223344'
            test_inst2.list_of_strs = 'jkl 556677'
            test_inst2.drop('list_of_strs', 'ghi 11223344')

            inst = SPARQLDict._get(klass=test_inst2.klass, inst_id=test_inst2.inst_id)
            self.assertNotIn('abc 778899', inst[utest.hasListOfStrs])
            self.assertNotIn('ghi 11223344', inst[utest.hasListOfStrs])
            self.assertIn('def 232324242525', inst[utest.hasListOfStrs])
            self.assertIn('jkl 556677', inst[utest.hasListOfStrs])
            self.assertEqual(len(inst[utest.hasListOfStrs]), 2)


    def test_29(self):
        with utest:
            rr1 = int(np.random.rand()*10**10)
            rr2 = int(np.random.rand()*10**10)
            rr3 = int(np.random.rand()*10**10)
            inst_id = f"utest.{int(np.random.rand()*10**10)}"
            test_inst10 = UnitTestNode1(inst_id=inst_id)
            test_inst10.keep_db_in_synch = True
            test_inst10.one_int = rr1
            test_inst10.list_of_int = rr2 
            test_inst10.list_of_int = rr3 
            test_inst10.one_str = f'my name {rr1}'
            test_inst10.list_of_strs = f'my name {rr2}'
            test_inst10.list_of_strs = f'my name {rr3}'

            insts = SPARQLDict._search(klass=UnitTestNode1.klass, how='all')
            self.assertIn(test_inst10.inst_id, [inst['ID'] for inst in insts])
            
    def test_30(self):
        with utest:
            rr1 = int(np.random.rand()*10**10)
            rr2 = int(np.random.rand()*10**10)
            rr3 = int(np.random.rand()*10**10)
            rr4 = int(np.random.rand()*10**10)
            rr5 = int(np.random.rand()*10**10)
            inst_id = f"utest.{int(np.random.rand()*10**10)}"
            test_inst10 = UnitTestNode1(inst_id=inst_id)
            test_inst10.keep_db_in_synch = True
            test_inst10.one_int = rr1
            test_inst10.list_of_ints = rr2 
            test_inst10.list_of_ints = rr3 
            test_inst10.list_of_ints = rr4 
            test_inst10.one_str = f'my name {rr1}'
            test_inst10.list_of_strs = f'my name {rr2}'
            test_inst10.list_of_strs = f'my name {rr3}'
            test_inst10.list_of_strs = f'my name {rr4}'

            insts = SPARQLDict._search(klass=UnitTestNode1.klass, how='all')
            nodes = UnitTestNode1.search(how='all')
            self.assertEqual(len(insts), len(nodes))

            node = UnitTestNode1.load_from_inst(inst=insts[-1])
            self.assertEqual(node.inst_id, insts[-1]['ID'])
            self.assertEqual([node.one_int], insts[-1][utest.hasOneInt])
            self.assertEqual(len(set(node.list_of_ints) & set(insts[-1][utest.hasListOfInts])), 3)
            self.assertIn(node.list_of_ints[0], insts[-1][utest.hasListOfInts])
            self.assertIn(node.list_of_ints[1], insts[-1][utest.hasListOfInts])
            self.assertIn(node.list_of_ints[2], insts[-1][utest.hasListOfInts])
            self.assertEqual([node.one_str], insts[-1][utest.hasOneStr])
            self.assertEqual(len(set(node.list_of_strs) & set(insts[-1][utest.hasListOfStrs])), 3)
            self.assertIn(node.list_of_strs[0], insts[-1][utest.hasListOfStrs])
            self.assertIn(node.list_of_strs[1], insts[-1][utest.hasListOfStrs])
            self.assertIn(node.list_of_strs[2], insts[-1][utest.hasListOfStrs])


    def test_31(self):
        with utest:
            rr1 = int(np.random.rand()*10**10)
            rr2 = int(np.random.rand()*10**10)
            rr3 = int(np.random.rand()*10**10)
            rr4 = int(np.random.rand()*10**10)
            rr5 = int(np.random.rand()*10**10)
            rr6 = int(np.random.rand()*10**10)
            rr7 = int(np.random.rand()*10**10)
            rr8 = int(np.random.rand()*10**10)
            inst_id10 = f"utest.{int(np.random.rand()*10**10)}"
            test_inst10 = UnitTestNode1(inst_id=inst_id10)
            test_inst10.keep_db_in_synch = True
            test_inst10.one_int = rr1
            test_inst10.list_of_ints = rr2 
            test_inst10.list_of_ints = rr3 
            test_inst10.one_str = f'my name {rr1}'
            test_inst10.list_of_strs = f'my name {rr2}'
            test_inst10.list_of_strs = f'my name {rr3}'


            inst_id11 = f"utest.{int(np.random.rand()*10**10)}"
            test_inst11 = UnitTestNode1(inst_id=inst_id11)
            test_inst11.keep_db_in_synch = True
            test_inst11.one_int = rr4
            test_inst11.list_of_ints = rr2 
            test_inst11.list_of_ints = rr5 
            test_inst11.one_str = f'my name {rr4}'
            test_inst11.list_of_strs = f'my name {rr2}'
            test_inst11.list_of_strs = f'my name {rr5}'


            inst_id12 = f"utest.{int(np.random.rand()*10**10)}"
            test_inst12 = UnitTestNode1(inst_id=inst_id12)
            test_inst12.keep_db_in_synch = True
            test_inst12.one_int = rr6
            test_inst12.list_of_ints = rr5 
            test_inst12.list_of_ints = rr7 
            test_inst12.list_of_ints = rr8 
            test_inst12.one_str = f'my name {rr6}'
            test_inst12.list_of_strs = f'my name {rr5}'
            test_inst12.list_of_strs = f'my name {rr7}'
            test_inst12.list_of_strs = f'my name {rr8}'

            insts = SPARQLDict._search(klass=UnitTestNode1.klass, props={utest.hasListOfInts:rr2},how='all')
            nodes = UnitTestNode1.search(props={utest.hasListOfInts:rr2}, how='all')
            self.assertEqual(len(insts), len(nodes))
            self.assertEqual(len(insts), 2)
            self.assertIn(insts[0]['ID'], [n.inst_id for n in nodes])
            self.assertIn(insts[1]['ID'], [n.inst_id for n in nodes])
            self.assertIn(test_inst10.inst_id, [n.inst_id for n in nodes])
            self.assertIn(test_inst11.inst_id, [n.inst_id for n in nodes])

            insts = SPARQLDict._search(klass=UnitTestNode1.klass, props={utest.hasListOfInts:rr5},how='all')
            nodes = UnitTestNode1.search(props={utest.hasListOfInts:rr5}, how='all')
            self.assertEqual(len(insts), len(nodes))
            self.assertEqual(len(insts), 2)
            self.assertIn(insts[0]['ID'], [n.inst_id for n in nodes])
            self.assertIn(insts[1]['ID'], [n.inst_id for n in nodes])
            self.assertIn(test_inst11.inst_id, [n.inst_id for n in nodes])
            self.assertIn(test_inst12.inst_id, [n.inst_id for n in nodes])

            insts = SPARQLDict._search(klass=UnitTestNode1.klass, props={utest.hasListOfInts:rr8},how='all')
            nodes = UnitTestNode1.search(props={utest.hasListOfInts:rr8}, how='all')
            self.assertEqual(len(insts), len(nodes))
            self.assertEqual(len(insts), 1)
            self.assertIn(insts[0]['ID'], [n.inst_id for n in nodes])
            self.assertIn(test_inst12.inst_id, [n.inst_id for n in nodes])


            insts = SPARQLDict._search(klass=UnitTestNode1.klass, props={utest.hasListOfInts:rr2},how='first')
            nodes = UnitTestNode1.search(props={utest.hasListOfInts:rr2}, how='first')
            self.assertEqual(len(insts), len(nodes))
            self.assertEqual(len(insts), 1)
            self.assertTrue((test_inst10.inst_id in [n.inst_id for n in nodes]) or (test_inst11.inst_id, [n.inst_id for n in nodes]))

            insts = SPARQLDict._search(klass=UnitTestNode1.klass, props={utest.hasListOfInts:rr5},how='first')
            nodes = UnitTestNode1.search(props={utest.hasListOfInts:rr5}, how='first')
            self.assertEqual(len(insts), len(nodes))
            self.assertEqual(len(insts), 1)
            self.assertIn(insts[0]['ID'], [n.inst_id for n in nodes])
            self.assertTrue((test_inst11.inst_id, [n.inst_id for n in nodes]) or (test_inst12.inst_id, [n.inst_id for n in nodes]))

            insts = SPARQLDict._search(klass=UnitTestNode1.klass, props={utest.hasListOfInts:rr8},how='first')
            nodes = UnitTestNode1.search(props={utest.hasListOfInts:rr8}, how='first')
            self.assertEqual(len(insts), len(nodes))
            self.assertEqual(len(insts), 1)
            self.assertIn(insts[0]['ID'], [n.inst_id for n in nodes])
            self.assertIn(test_inst12.inst_id, [n.inst_id for n in nodes])

    def test_32(self):
        with utest:
            rr1 = int(np.random.rand()*10**10)
            rr2 = int(np.random.rand()*10**10)
            rr3 = int(np.random.rand()*10**10)
            rr4 = int(np.random.rand()*10**10)
            test_inst10 = UnitTestNode1()
            test_inst10.keep_db_in_synch = False
            test_inst10.one_int = rr1
            test_inst10.list_of_ints = rr2 
            test_inst10.list_of_ints = rr3 
            test_inst10.list_of_ints = rr4 
            test_inst10.one_str = f'my name {rr1}'
            test_inst10.list_of_strs = f'my name {rr2}'
            test_inst10.list_of_strs = f'my name {rr3}'
            test_inst10.list_of_strs = f'my name {rr4}'

            test_inst10.save()

            test_inst10_copy = UnitTestNode1(inst_id=test_inst10.inst_id)
            self.assertEqual(rr1, test_inst10_copy.one_int)
            self.assertEqual(len(test_inst10_copy.list_of_ints), 3)
            self.assertIn(rr2, test_inst10_copy.list_of_ints)
            self.assertIn(rr3, test_inst10_copy.list_of_ints)
            self.assertIn(rr4, test_inst10_copy.list_of_ints)
            self.assertEqual(f'my name {rr1}', test_inst10_copy.one_str)
            self.assertEqual(len(test_inst10_copy.list_of_strs), 3)
            self.assertIn(f'my name {rr2}', test_inst10_copy.list_of_strs)
            self.assertIn(f'my name {rr3}', test_inst10_copy.list_of_strs)
            self.assertIn(f'my name {rr4}', test_inst10_copy.list_of_strs)

    def test_33(self):
        with utest:
            rr1 = int(np.random.rand()*10**10)
            rr2 = int(np.random.rand()*10**10)
            rr3 = int(np.random.rand()*10**10)
            rr4 = int(np.random.rand()*10**10)
            test_inst10 = UnitTestNode1()
            test_inst10.keep_db_in_synch = True
            test_inst10.one_int = rr1
            test_inst10.list_of_ints = rr2 
            test_inst10.list_of_ints = rr3 
            test_inst10.one_str = f'my name {rr1}'
            test_inst10.list_of_strs = f'my name {rr2}'
            test_inst10.keep_db_in_synch = False
            test_inst10.list_of_ints = rr4 
            test_inst10.list_of_strs = f'my name {rr3}'
            test_inst10.list_of_strs = f'my name {rr4}'

            test_inst10.save()

            test_inst10_copy = UnitTestNode1(inst_id=test_inst10.inst_id)
            self.assertEqual(rr1, test_inst10_copy.one_int)
            self.assertEqual(len(test_inst10_copy.list_of_ints), 3)
            self.assertIn(rr2, test_inst10_copy.list_of_ints)
            self.assertIn(rr3, test_inst10_copy.list_of_ints)
            self.assertIn(rr4, test_inst10_copy.list_of_ints)
            self.assertEqual(f'my name {rr1}', test_inst10_copy.one_str)
            self.assertEqual(len(test_inst10_copy.list_of_strs), 3)
            self.assertIn(f'my name {rr2}', test_inst10_copy.list_of_strs)
            self.assertIn(f'my name {rr3}', test_inst10_copy.list_of_strs)
            self.assertIn(f'my name {rr4}', test_inst10_copy.list_of_strs)


    def test_34(self):
        with utest:
            rr1 = int(np.random.rand()*10**10)
            rr2 = int(np.random.rand()*10**10)
            rr3 = int(np.random.rand()*10**10)
            rr4 = int(np.random.rand()*10**10)
            test_inst10 = UnitTestNode1()
            test_inst10.keep_db_in_synch = False
            test_inst10.one_int = rr1
            test_inst10.list_of_ints = rr2 
            test_inst10.list_of_ints = rr3 
            test_inst10.one_str = f'my name {rr1}'
            test_inst10.list_of_strs = f'my name {rr2}'
            test_inst10.keep_db_in_synch = True
            test_inst10.list_of_ints = rr4 
            test_inst10.list_of_strs = f'my name {rr3}'
            test_inst10.list_of_strs = f'my name {rr4}'

            test_inst10.save()

            test_inst10_copy = UnitTestNode1(inst_id=test_inst10.inst_id)
            self.assertEqual(rr1, test_inst10_copy.one_int)
            self.assertEqual(len(test_inst10_copy.list_of_ints), 3)
            self.assertIn(rr2, test_inst10_copy.list_of_ints)
            self.assertIn(rr3, test_inst10_copy.list_of_ints)
            self.assertIn(rr4, test_inst10_copy.list_of_ints)
            self.assertEqual(f'my name {rr1}', test_inst10_copy.one_str)
            self.assertEqual(len(test_inst10_copy.list_of_strs), 3)
            self.assertIn(f'my name {rr2}', test_inst10_copy.list_of_strs)
            self.assertIn(f'my name {rr3}', test_inst10_copy.list_of_strs)
            self.assertIn(f'my name {rr4}', test_inst10_copy.list_of_strs)

    def test_35(self):
        # test drop() in different scenarios
        with utest:
            test_inst2 = UnitTestNode1(keep_db_in_synch = True)
            test_inst2.list_of_strs = 'abc'
            test_inst2.list_of_strs = 'dfe'
            test_inst2.list_of_strs = 'ghi'
            test_inst2.one_str = 'abc'
            test_inst2.one_int = 9999

            test_inst2.drop('list_of_strs', 'dfe')
            test_inst2.drop('one_int', 9999)
        
            inst = SPARQLDict._get(klass=UnitTestNode1, inst_id=test_inst2.inst_id)
            self.assertNotIn('dfe', test_inst2.list_of_strs)
            self.assertNotIn('dfe', inst[utest.hasListOfStrs])
            self.assertIsNone(test_inst2.one_int)
            self.assertNotIn(utest.hasOneInt, inst.keys())

            test_inst2.drop('list_of_strs')
            test_inst2.drop('one_int')

            inst = SPARQLDict._get(klass=UnitTestNode1, inst_id=test_inst2.inst_id)
            self.assertNotIn(utest.hasListOfStrs, inst.keys())
            self.assertNotIn(utest.hasOneInt, inst.keys())

            test_inst2.one_int = 1010
            inst = SPARQLDict._get(klass=UnitTestNode1, inst_id=test_inst2.inst_id)
            self.assertEqual(test_inst2.one_int, 1010)
            self.assertEqual(inst[utest.hasOneInt], [1010])

            inst = SPARQLDict._get(klass=UnitTestNode1, inst_id=test_inst2.inst_id)
            test_inst2.drop('one_int')
            inst = SPARQLDict._get(klass=UnitTestNode1, inst_id=test_inst2.inst_id)
            self.assertNotIn(utest.hasOneInt, inst.keys())


if __name__ == '__main__':
    unittest.main(exit=False)
