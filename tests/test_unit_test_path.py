import unittest
from src.py2graphdb.utils.misc_lib import *
import os

from src.py2graphdb.config import config as CONFIG

if os.path.exists(CONFIG.LOG_FILE):
    os.remove(CONFIG.LOG_FILE)

from owlready2 import default_world, onto_path
onto_path.append('input/ontology_cache/')

utest = default_world.get_ontology(CONFIG.NM)

CONFIG.STORE_LOCAL = False
with utest:
    from pprint import pprint
    import numpy as np
    from src.py2graphdb.utils.db_utils import SPARQLDict
    from tests.unit_test_ks import UnitTestNode1, UnitTestNode2, UnitTestNode3
    print()



def build_test_nodes(n):
    return [UnitTestNode1(inst_id=f'utest.n{i}', keep_db_in_synch = True) for i in range(1,n+1)]

def delete_test_nodes(n):
    return [UnitTestNode1(inst_id=f'utest.n{i}', keep_db_in_synch = True).delete() for i in range(1,n+1)]

def init_test_nodes(n):

    # build_test_nodes(n)
    delete_test_nodes(n)
    return build_test_nodes(n)

class TestConfig():
    def __init__(self, config_n):
        if config_n == 1:
            self.init_test_config_1()
        elif config_n == 2:
            self.init_test_config_2()
        else:
            raise ValueError("Invalid config_n, must be in [1, 2]")

    # Network configuration 1
    nodes = []
    def init_test_config_1(self):
        with utest:
            n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11 = init_test_nodes(11)
            # n1 -> n5 -> n3 -> n9
            n1.list_of_uris = n5.inst_id
            n5.list_of_uris = n3.inst_id
            n3.list_of_uris = n9.inst_id

            # n1 -> n7 -> n2 -> n4 -> n9
            n1.list_of_uris = n7.inst_id
            n7.list_of_uris = n2.inst_id
            n2.list_of_uris = n4.inst_id
            n4.list_of_uris = n9.inst_id
            self.nodes = [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11]

    # Network configuration 2
    def init_test_config_2(self):
        with utest:
            n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11 = init_test_nodes(11)
            n1.one_int = 1
            n4.one_int = 3
            n3.one_int = 3
            n9.one_int = 1
            # n1 -> n5 -> n3 -> n9
            n1.list_of_uris = n5.inst_id
            n5.list_of_uris = n3.inst_id
            n3.list_of_uris = n9.inst_id

            # n1 -> n7 -> n2 -> n4 -> n9
            n1.list_of_uris = n7.inst_id
            n7.list_of_uris = n2.inst_id
            n2.list_of_uris = n4.inst_id
            n4.list_of_uris = n9.inst_id
        self.nodes = [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11]

class TestUnitTestPathConfig1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # save classes and methods in graph
        from graphdb_importer import import_and_wait, set_config
        TMP_DIR = './tmp/'
        _ = os.makedirs(TMP_DIR) if not os.path.exists(TMP_DIR) else None
        owl_file = f'{TMP_DIR}unit_test_path1.owl'
        utest.save(owl_file)
        set_config(CONFIG.SERVER_URL, CONFIG.REPOSITORY, username='admin', password='admin')
        import_and_wait(owl_file, replace_graph=True)

        SPARQLDict._clear_graph(graph=CONFIG.GRAPH_NAME)

        _ = TestConfig(config_n=1)

    def test_1(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='collect', direction='children', how='all')
            assert res == [
                {'end': 'utest.n9', 'path': ['utest.n7', 'utest.n2', 'utest.n4'], 'start': 'utest.n1'},
                {'end': 'utest.n9', 'path': ['utest.n5', 'utest.n3'], 'start': 'utest.n1'}]
            

    def test_2(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='collect', direction='children', how='first')
            self.assertEqual( res ,  {'end': 'utest.n9', 'path': ['utest.n5', 'utest.n3'], 'start': 'utest.n1'})

        with utest:   
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='collect', direction='children', how='shortest')
            self.assertEqual( res ,  [{'end': 'utest.n9', 'path': ['utest.n5', 'utest.n3'], 'start': 'utest.n1'}])

    def test_3(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='ask', direction='children', how='all')
            self.assertTrue(res)

    def test_4(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n6'
            res = SPARQLDict._process_path_request(start, end, action='ask', direction='children', how='all')
            self.assertFalse(res)

    def test_5(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n4'
            res = SPARQLDict._process_path_request(start, end, action='distance', direction='children', how='all')
            self.assertEqual( res ,  [{'distance': 3, 'end': 'utest.n4', 'start': 'utest.n1'}])

    def test_6(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='collect', preds=[utest.hasListOfURIs], direction='children', how='all')
            self.assertEqual(res, [
                {'end': 'utest.n9', 'path': ['utest.n7', 'utest.n2', 'utest.n4'], 'start': 'utest.n1'},
                {'end': 'utest.n9', 'path': ['utest.n5', 'utest.n3'], 'start': 'utest.n1'}]
            )


    def test_7(self):
        with utest:
            start = 'utest.n9'
            end = 'utest.n1'
            res = SPARQLDict._process_path_request(start, end, action='collect', preds=[utest.hasListOfURIs], direction='parents', how='all')
            self.assertEqual(res, [
                {'end': 'utest.n1', 'path': ['utest.n4', 'utest.n2', 'utest.n7'], 'start': 'utest.n9'},
                {'end': 'utest.n1', 'path': ['utest.n3', 'utest.n5'], 'start': 'utest.n9'}]
            )
            

    def test_8(self):
        with utest:
            start = 'utest.n9'
            end = 'utest.n1'
            res = SPARQLDict._process_path_request(start, end, action='collect', preds=[utest.hasListOfURIs], direction='parents', how='first')
            assert res == {'end': 'utest.n1', 'path': ['utest.n3', 'utest.n5'], 'start': 'utest.n9'}
            


    def test_9(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='distance', preds=[utest.hasListOfURIs], direction='children', how='all')
            self.assertEqual( res ,  [{'distance': 3, 'end': 'utest.n9', 'start': 'utest.n1'}])

    def test_10(self):
        with utest:
            start = 'utest.n1'
            end = [utest.hasListOfURIs]
            res = SPARQLDict._process_path_request(start, end, action='distance', direction='children', how='all')
            self.assertEqual(res, [
                {'distance': 1, 'end': 'utest.n5', 'start': 'utest.n1'},
                {'distance': 1, 'end': 'utest.n7', 'start': 'utest.n1'},
                {'distance': 2, 'end': 'utest.n2', 'start': 'utest.n1'},
                {'distance': 2, 'end': 'utest.n3', 'start': 'utest.n1'},
                {'distance': 3, 'end': 'utest.n4', 'start': 'utest.n1'}]
            )


    def test_11(self):
        with utest:
            start = 'utest.n1'
            end = [utest.hasListOfURIs]
            res = SPARQLDict._process_path_request(start, end, action='distance', direction='children', how='first')
            self.assertEqual( res ,  [{'start': 'utest.n1', 'end': 'utest.n2', 'distance': 2}])

    def test_12(self):
        with utest:
            start = 'utest.n9'
            end = 'utest.n1'
            res = SPARQLDict._process_path_request(start, end, action='distance', preds=[utest.hasListOfURIs], direction='parents', how='first')
            self.assertEqual( res ,  [{'distance': 3, 'end': 'utest.n1', 'start': 'utest.n9'}])

        with utest:    
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='collect', preds=[utest.hasListOfURIs], direction='parents', how='all')
            self.assertEqual( res ,  [])

    def test_13(self):
        with utest:
            start = 'utest.n9'
            end = 'utest.n1'
            res = SPARQLDict._process_path_request(start, end, action='collect', preds=[utest.hasListOfURIs], direction='children', how='all')
            self.assertEqual( res ,  [])

    def test_14(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='ask', preds=[utest.hasListOfURIs], direction='children', how='all')
            self.assertTrue(res)

        with utest:    
            start = 'utest.n9'
            end = 'utest.n1'
            res = SPARQLDict._process_path_request(start, end, action='ask', preds=[utest.hasListOfURIs], direction='parents', how='first')
            self.assertTrue(res)

    def test_15(self):
        with utest:
            start = 'utest.n1'
            end = 'utest.n9'
            res = SPARQLDict._process_path_request(start, end, action='ask', preds=[utest.hasListOfURIs], direction='parents', how='all')
            self.assertFalse(res)

    def test_16(self):
        with utest:
            start = 'utest.n9'
            end = 'utest.n1'
            res = SPARQLDict._process_path_request(start, end, action='ask', preds=[utest.hasListOfURIs], direction='children', how='all')
            self.assertFalse(res)


class TestUnitTestPathConfig2(unittest.TestCase):
    # Network configuration 2
    ################

    @classmethod
    def setUpClass(cls):
        # save classes and methods in graph
        from graphdb_importer import import_and_wait, set_config
        TMP_DIR = './tmp/'
        _ = os.makedirs(TMP_DIR) if not os.path.exists(TMP_DIR) else None
        owl_file = f'{TMP_DIR}unit_test_path2.owl'
        utest.save(owl_file)
        set_config(CONFIG.SERVER_URL, CONFIG.REPOSITORY, username='admin', password='admin')
        import_and_wait(owl_file, replace_graph=True)

        SPARQLDict._clear_graph(graph=CONFIG.GRAPH_NAME)
        _ = TestConfig(config_n=2)

    def test_20(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:1}
            res = SPARQLDict._process_path_request(start, end, action='collect', direction='children', how='all')
            self.assertEqual(res, [
                {'start': 'utest.n1', 'end': 'utest.n9', 'path': ['utest.n7', 'utest.n2', 'utest.n4']}, 
                {'start': 'utest.n1', 'end': 'utest.n9', 'path': ['utest.n5', 'utest.n3']}]
            )


    def test_18(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:1}
            res = SPARQLDict._process_path_request(start, end, action='ask', direction='children', how='all')
            self.assertTrue(res)


    def test_19(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:1}
            res = SPARQLDict._path_exists(start, end, direction='children')
            self.assertTrue(res)

    def test_20(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:10}
            res = SPARQLDict._process_path_request(start, end, action='collect', direction='children', how='all')
            self.assertEqual( res ,  [])


    def test_20(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:10}
            res = SPARQLDict._process_path_request(start, end, action='ask', direction='children', how='all')
            self.assertFalse(res)


    def test_21(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:10}
            res = SPARQLDict._path_exists(start, end, direction='children')
            self.assertFalse(res)


    def test_22(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:10}
            res = SPARQLDict._process_path_request(start, end, action='collect', direction='children', how='first')
            self.assertIsNone(res)


    def test_23(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:10}
            res = SPARQLDict._process_path_request(start, end, action='ask', direction='children', how='first')
            self.assertFalse(res)


    def test_24(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:10}
            res = SPARQLDict._path_exists(start, end, direction='children')
            self.assertFalse(res)


    def test_25(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:3}
            res = SPARQLDict._process_path_request(start, end, action='collect', direction='children', how='all')
            self.assertEqual(res, [
                {'start': 'utest.n1', 'end': 'utest.n4', 'path': ['utest.n7', 'utest.n2']}, 
                {'start': 'utest.n1', 'end': 'utest.n3', 'path': ['utest.n5']}]
            )


    def test_26(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:3}
            res = SPARQLDict._process_path_request(start, end, action='ask', direction='children', how='all')
            self.assertTrue(res)


    def test_27(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:3}
            res = SPARQLDict._path_exists(start, end, direction='children')
            self.assertTrue(res)


    def test_28(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:3}
            res = SPARQLDict._process_path_request(start, end, action='collect', direction='children', how='first')
            self.assertEqual( res ,  {'start': 'utest.n1', 'end': 'utest.n4', 'path': ['utest.n7', 'utest.n2']})


    def test_29(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:3}
            res = SPARQLDict._process_path_request(start, end, action='ask', direction='children', how='first')
            self.assertTrue(res)


    def test_30(self):
        with utest:
            start = 'utest.n1'
            end = {utest.hasOneInt:3}
            res = SPARQLDict._path_exists(start, end, direction='children')
            self.assertTrue(res)

if __name__ == '__main__':
    unittest.main(exit=False)
