from __main__ import *
from src.Models.graph_node import GraphNode
from src.utils.db_utils import PropertyList, SPARQLDict, Thing
from owlready2 import default_world, ObjectProperty, DataProperty, rdfs, Thing 
from config import config as CONFIG
utest = default_world.get_ontology(CONFIG.NM)
from src.utils.db_utils import PropertyList, SPARQLDict, resolve_nm_for_dict, Thing

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

    class hasOneURI(ObjectProperty):
        rdfs.comment = ["Desc for the object"]
        range = [Thing]

    class hasListOfURIs(ObjectProperty):
        rdfs.comment = ["Desc for the object"]
        range = [Thing]

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
        A db Model class that defines the schema for Traces.
        Instances of this class are created whenever a new hypothesis is created.

        ...

        Attributes
        ----------
        __tablename__ : str
            The name of the database table
        id : SQLAlchemy.Column
            A unique ID for the knowledge source type
        created_at : SQLAlchemy.Column
            The date and time when an instantiated
        hypothesis : SQLAlchemy.relationship
            Relationship with the hypothesis data level
    """
    klass = 'utest.UnitTestNode1'
    relations = {
        'list_of_ints' : {'pred':utest.hasListOfInts, 'cardinality':'many'},
        'list_of_floats' : {'pred':utest.hasListOfFloats, 'cardinality':'many'},
        'list_of_strs' : {'pred':utest.hasListOfStrs, 'cardinality':'many'},
        'list_of_uris' : {'pred':utest.hasListOfURIs, 'cardinality':'many'},
        'one_int' : {'pred':utest.hasOneInt, 'cardinality':'one'},
        'one_float' : {'pred':utest.hasOneFloat, 'cardinality':'one'},
        'one_str' : {'pred':utest.hasOneStr, 'cardinality':'one'},
        'one_uri' : {'pred':utest.hasOneURI, 'cardinality':'one'},
    }

    def __init__(self, inst_id=None, keep_db_in_synch=False) -> None:
        super().__init__(inst_id=inst_id, keep_db_in_synch=keep_db_in_synch)

        

    imported_code = open('src/utils/_model_getters_setters_deleters.py').read()
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

    def __init__(self, inst_id=None, keep_db_in_synch=False) -> None:
        super().__init__(inst_id=inst_id, keep_db_in_synch=keep_db_in_synch)


    imported_code = open('src/utils/_model_getters_setters_deleters.py').read()
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

    def __init__(self, inst_id=None, keep_db_in_synch=False) -> None:
        super().__init__(inst_id=inst_id, keep_db_in_synch=keep_db_in_synch)


    imported_code = open('src/utils/_model_getters_setters_deleters.py').read()
    exec(imported_code)

