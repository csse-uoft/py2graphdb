# py2graphdb
Python wrapper for GraphDB and SPARQL interface

Required [OntoText](https://www.ontotext.com/products/graphdb/download) installed locally, running on [http://localhost:7200](http://localhost:7200). This can be changed in the [config/unit_test_config.yml](config/unit_test_config.yml) file)
# Introduction
py2graphdb is a Python-SPARQL interface that allows manipultion of RDF-based triple store database to be maniplated as Python objects. 

```python
from py2graphdb.Model import NodeGraph
from py2graphdb.utils.db_utils import SPARQLDict
from owlready2 import ObjectProperty, DataProperty, rdfs

utest = default_world.get_ontology('utest')
with utest:
  class hasName(DataProperty):
      range = [str]
  class hasNumbers(DataProperty):
      range = [int]
  class hasListOfNodes(ObjectProperty):
      range = [Thing]


class MyNode(NodeGraph):
  ...
  klass = 'utest.MyNode'
  relations = {
      'name'       : {'pred':utest.hasName, 'cardinality':'one'},
      'my_numbers' : {'pred':utest.hasNumbers, 'cardinality':'many'},
      'my_nodes'   : {'pred':utest.hasListOfNodes, 'cardinality':'many'}
  }

# creates a new node object and keeps its properties synched up with the database.
my_node = MyNode(inst_id='parent_node', keep_db_synch=True) 
# if no inst_id is provided, a UUID is generated.
# >> triples stored in the database:
#    utest:parent_node  rdf:type               utest:MyNode.

# set name property (cardinality:one)
my_node.name = "My First Node"
# >> triples stored in the database:
#    utest:parent_node  utest:hasName          "My First Node"^^xsd:string.

# add list of numbers (cardinality:many)
my_node.my_numbers = 123
my_node.my_numbers = 456
# >> triples stored in the database:
#    utest:parent_node  utest:hasNumbers         123^^xsd:integer.
#    utest:parent_node  utest:hasNumbers         456^^xsd:integer.


# connect object nodes
my_node.my_nodes = MyNode(inst_id='child1', keep_db_synch=True)
my_node.my_nodes = MyNode(inst_id='child2', keep_db_synch=True)
# >> triples stored in the database:
#    utest:child1       rdf:type               utest:MyNode.
#    utest:parent_node  utest:hasListOfNodes   utest:child1.
#    utest:child2       rdf:type               utest:MyNode.
#    utest:parent_node  utest:hasListOfNodes   utest:child2.
```

### Supports Search by properties
```python
# find parent node if it has any of the node in the list (hasany)
node = MyNode.search(props={hasany(utest.hasListOfNodes):['utest.child1', 'utest.child2', 'utest.child3'], how='all')
print(node) # >> [utest.main_node]

# find parent node if it has all of the nodes in the list (hasall)
nodes = MyNode.search(props={hasall(utest.hasListOfNodes):['utest.child1', 'utest.child2', 'utest.child3'], how='all')
print(nodes) # >> None

```
### Supports Search by graph traversal
```python
res = SPARQLDict._process_path_request(my_node, 'utest.abc', action='ask', direction='children', how='all')
print(res) # >> False

res = SPARQLDict._process_path_request(my_node, 'utest.child1', action='ask', direction='children', how='all')
print(res) # >> True

res = SPARQLDict._process_path_request(my_node, 'utest.child1', action='collect', direction='children', how='all')
print(res) # >> [utest.child1]

```


## Setup
`conda env create -f Py2GraphDB.yml`

## To run example
`conda activate Py2GraphDB`

`python -m src.py2graphdb.main`

## To run unit tests
`conda activate Py2GraphDB`

`python -m unittest`
