from __main__ import *
from src.py2graphdb.config import config as CONFIG
from owlready2 import default_world, ObjectProperty, DataProperty, rdfs , onto_path, Thing
import os
if os.path.exists(CONFIG.LOG_FILE): 
  os.remove(CONFIG.LOG_FILE)
CONFIG.STORE_LOCAL = False
from src.py2graphdb.ontology.operators import *

utest = default_world.get_ontology(CONFIG.NM)
import unittest
from src.py2graphdb.utils.misc_lib import *

with utest:
    import numpy as np
    from pprint import pprint
    from src.py2graphdb.utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, _resolve_nm
    from tests.unit_test_ks import OrganizationNode, LogicModelNode, ProgramNode, ServiceNode, ActivityNode

def delete_test_nodes():
    OrganizationNode(inst_id=f'utest.1000', keep_db_in_synch = True).delete()
    LogicModelNode(inst_id=f'utest.1001', keep_db_in_synch = True).delete()
    ProgramNode(inst_id=f'utest.1002', keep_db_in_synch = True).delete()
    ServiceNode(inst_id=f'utest.1003', keep_db_in_synch = True).delete()
    ActivityNode(inst_id=f'utest.1004', keep_db_in_synch = True).delete()

class TestConfig():
    def __init__(self):
        self.init_impact_model()

    def init_impact_model(self):
        with utest:
            delete_test_nodes()
            organization = OrganizationNode(inst_id=f'utest.1000', keep_db_in_synch = True)
            logic_model = LogicModelNode(inst_id=f'utest.1001', keep_db_in_synch = True)
            program = ProgramNode(inst_id=f'utest.1002', keep_db_in_synch = True)
            service = ServiceNode(inst_id=f'utest.1003', keep_db_in_synch = True)
            activity = ActivityNode(inst_id=f'utest.1004', keep_db_in_synch = True)

            logic_model.organization = organization.inst_id
            logic_model.program = program.inst_id
            program.service = service.inst_id
            service.activity = activity.inst_id
            
            #organization -> logic_model -> program -> service -> activity

class TestImpactModel(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        #save classes and methods in graph
        from graphdb_importer import import_and_wait, set_config
        TMP_DIR = './tmp/'
        _ = os.makedirs(TMP_DIR) if not os.path.exists(TMP_DIR) else None
        owl_file = f'{TMP_DIR}unit_test_impact.owl'
        #breakpoint()
        utest.save(owl_file)
        set_config(CONFIG.SERVER_URL, CONFIG.REPOSITORY, username='admin', password='admin')
        import_and_wait(owl_file, replace_graph=True)

        SPARQLDict._clear_graph(graph=CONFIG.GRAPH_NAME)

        _ = TestConfig()
    
    def test_path_basic(self):
        with utest:
            start = 'utest.1001'
            end = 'utest.1004'
            preds = [utest.forOrganization, utest.hasProgram, utest.hasService, utest.hasSubActivity]
            res = SPARQLDict._process_path_request(start, end, action='collect', preds=preds, direction='children', how='all')
            self.assertEqual(res, [{'start': 'utest.1001', 'end': 'utest.1004', 'path': ['utest.1002', 'utest.1003']}])

    def test_path_no_end(self):
        with utest:
            start = 'utest.1001'
            preds = [utest.forOrganization, utest.hasProgram, utest.hasService, utest.hasSubActivity]
            res = SPARQLDict._process_path_request(start, None, action='collect', preds=preds, direction='children', how='all')
            self.assertEqual(res, [{'start': 'utest.1001', 'end': 'utest.1004', 'path': ['utest.1002', 'utest.1003']}, 
                                    {'start': 'utest.1001', 'end': 'utest.1003', 'path': ['utest.1002']},
                                     {'start': 'utest.1001', 'end': 'utest.1002', 'path': []},
                                      {'start': 'utest.1001', 'end': 'utest.1000', 'path': []}])

    def test_path_reverse(self):
        with utest:    
            start = 'utest.1004'
            end = 'utest.1001'
            preds = [utest.forOrganization, utest.hasProgram, utest.hasService, utest.hasSubActivity]
            res = SPARQLDict._process_path_request(start, end, action='collect', preds=preds, direction='parents', how='all')
            self.assertEqual(res, [{'start': 'utest.1004', 'end': 'utest.1001', 'path': ['utest.1003', 'utest.1002']}])


    def test_path_not_exist(self):
        with utest:    
            start = 'utest.1004'
            end = 'utest.1002'
            preds = [utest.forOrganization, utest.hasProgram, utest.hasService, utest.hasSubActivity]
            res = SPARQLDict._process_path_request(start, end, action='ask', preds=preds, direction='children', how='all')
            self.assertFalse(res)

    def test_path_distance(self):
        with utest:
            start = 'utest.1001'
            end = 'utest.1004'
            preds = [utest.forOrganization, utest.hasProgram, utest.hasService, utest.hasSubActivity]
            res = SPARQLDict._process_path_request(start, end, action='distance', preds=preds, direction='children', how='all')
            self.assertEqual(res, [{'start': 'utest.1001', 'end': 'utest.1004', 'distance': 3}])

if __name__ == '__main__':
    unittest.main(exit=False)


    
