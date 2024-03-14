from __main__ import *
from src.py2graphdb.Models.graph_node import GraphNode
from src.py2graphdb.utils.db_utils import PropertyList, SPARQLDict, Thing
from owlready2 import default_world, ObjectProperty, DataProperty, rdfs, Thing 
from src.py2graphdb.ontology.operators import *
from src.py2graphdb.config import config as CONFIG
utest = default_world.get_ontology(CONFIG.NM)
from src.py2graphdb.utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, Thing, _resolve_nm

with utest:
    class hasOneStr(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [str]

    class hasListOfStrs(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [str]

    class hasOneInt(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [int]

    class hasListOfInts(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [int]

    class hasOneBool(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [bool]

    class hasListOfBools(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [bool]

    class hasOneURI(ObjectProperty):
        rdfs.comment = ["Desc for the object"]
        range = [Thing]

    class hasListOfURIs(ObjectProperty):
        rdfs.comment = ["Desc for the object"]
        range = [Thing]

    class forOneURI(ObjectProperty):
        rdfs.comment = ["Desc for the object"]
        range = [Thing]
        inverse_property = hasListOfURIs


    class forListOfURIs(ObjectProperty):
        rdfs.comment = ["Desc for the object"]
        range = [Thing]
        inverse_property = hasOneURI

    

    class hasOneFloat(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [float]

    class hasListOfFloats(DataProperty):
        rdfs.comment = ["Desc for the object"]
        range = [float]
        

    class hasOneInt2(DataProperty):
        rdfs.comment = ["Desc for subclass object at level 2"]
        range = [int]

    class hasListOfInts2(DataProperty):
        rdfs.comment = ["Desc for subclass object at level 2"]
        range = [int]


    class hasOneInt3(DataProperty):
        rdfs.comment = ["Desc for subclass object at level 3"]
        range = [int]

    class hasListOfInts3(DataProperty):
        rdfs.comment = ["Desc for subclass object at level 3"]
        range = [int]


import re
class UnitTestNode1(GraphNode):
    """

        ...

        Attributes
        ----------
    """
    klass = 'utest.UnitTestNode1'
    relations = {
        'list_of_ints' : {'pred':utest.hasListOfInts, 'cardinality':'many'},
        'list_of_floats' : {'pred':utest.hasListOfFloats, 'cardinality':'many'},
        'list_of_strs' : {'pred':utest.hasListOfStrs, 'cardinality':'many'},
        'list_of_uris' : {'pred':utest.hasListOfURIs, 'cardinality':'many'},
        'list_of_bools' : {'pred':utest.hasListOfBools, 'cardinality':'many'},
        'one_int' : {'pred':utest.hasOneInt, 'cardinality':'one'},
        'one_float' : {'pred':utest.hasOneFloat, 'cardinality':'one'},
        'one_str' : {'pred':utest.hasOneStr, 'cardinality':'one'},
        'one_uri' : {'pred':utest.hasOneURI, 'cardinality':'one'},
        'one_bool' : {'pred':utest.hasOneBool, 'cardinality':'one'},
    }

    def __init__(self, inst_id=None, inst=None, keep_db_in_synch=False) -> None:
        super().__init__(inst_id=inst_id, inst=inst, keep_db_in_synch=keep_db_in_synch)

        
    # from src.py2graphdb.utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, Thing
    imported_code = open('./src/py2graphdb/utils/_model_getters_setters_deleters.py').read()
    exec(imported_code)


class UnitTestNode2(UnitTestNode1):
    """
    A db Model class that defines the schema for the Ner data level.
    Base schema is extended from the Hypothesis class.

    ...

    Attributes
    ----------
    __tablename__ : str
        The name of the database table
    phrase_id : SQLAlchemy.Column
        The ID of the Phrase used as the subject of the NER hypothesis
    phrase : SQLAlchemy.relationship
        Relationship with the associated phrase
    entity : SQLAlchemy.Column
        Entity type assigned to this phrase

    """
    klass = 'utest.UnitTestNode2'
    super_relations = UnitTestNode1.relations    
    klass_relations = {
        'one_int_level2' : {'pred':utest.hasOneInt2, 'cardinality':'one'},
        'list_of_ints_level2' : {'pred':utest.hasListOfInts2, 'cardinality':'many'},
    }
    relations = {**klass_relations, **super_relations}

    def __init__(self, inst_id=None, inst=None, keep_db_in_synch=False) -> None:
        super().__init__(inst_id=inst_id, inst=inst, keep_db_in_synch=keep_db_in_synch)


    # from src.py2graphdb.utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, Thing
    imported_code = open('src/py2graphdb/utils/_model_getters_setters_deleters.py').read()
    exec(imported_code)


class UnitTestNode3(UnitTestNode2):
    """
    A db Model class that defines the schema for the Ner data level.
    Base schema is extended from the Hypothesis class.

    ...

    Attributes
    ----------
    __tablename__ : str
        The name of the database table
    phrase_id : SQLAlchemy.Column
        The ID of the Phrase used as the subject of the NER hypothesis
    phrase : SQLAlchemy.relationship
        Relationship with the associated phrase
    entity : SQLAlchemy.Column
        Entity type assigned to this phrase

    """
    klass = 'utest.UnitTestNode3'
    super_relations = UnitTestNode2.relations    
    klass_relations = {
        'one_int_level3' : {'pred':utest.hasOneInt3, 'cardinality':'one'},
        'list_of_ints_level3' : {'pred':utest.hasListOfInts3, 'cardinality':'many'},
    }
    relations = {**klass_relations, **super_relations}

    def __init__(self, inst_id=None, inst=None, keep_db_in_synch=False) -> None:
        super().__init__(inst_id=inst_id, inst=inst, keep_db_in_synch=keep_db_in_synch)


    # from src.py2graphdb.utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, Thing
    imported_code = open('src/py2graphdb/utils/_model_getters_setters_deleters.py').read()
    exec(imported_code)



