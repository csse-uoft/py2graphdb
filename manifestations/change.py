"""
TOVE Change Module

Creator: Mark Fox
Version: 0.1
Date: 9 February 2021
License: Creative Commons

The TOVE Change module provides OWLReady2-based functions for manipulating Manifestations
based on the resource ontology defined in:

http://ontology.eil.utoronto.ca/5087/Change.owl


"""
import unittest
from owlready2 import *
from utils import pLog
import otime
from py2graphdb.Models.graph_node import GraphNode
from owlready2 import ObjectProperty, DataProperty, rdfs
from datetime import time
import datetime
from datetime import datetime
import unittest
from unittest.mock import MagicMock


# global variables
Change = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Change.owl')
Resource = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Resource.owl')
I72 = get_ontology('http://ontology.eil.utoronto.ca/5087/1/iso21972.owl')
Time = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Time.owl')
owltime = get_namespace('http://www.w3.org/2006/time')
xsd = get_namespace('http://www.w3.org/2001/XMLSchema')

with Change:
  class hasA(DataProperty):
      range = [str]
  class hasNameSpace(DataProperty):
      range = [str]
  class hasType(DataProperty):
      range = [int]
  class existsAt(DataProperty):
      range = [int]
  class hasNode(ObjectProperty):
      range = [Thing]

class ManifestationNode(GraphNode):
  klass = 'Manifestation'
  relations = {
      'is_a': {'pred': Change.hasA, 'cardinality':'many'},
      'nameSpace': {'pred': Change.hasNameSpace, 'cardinality': 'one'},
      'primaryType': {'pred':Change.hasType, 'cardinality':'one'},
      'existsAt': {'pred':Change.existsAt, 'cardinality':'one'},
      'hasFirstManifestation' : {'pred':Change.hasNode, 'cardinality':'one'},
      'hasLastManifestation' : {'pred':Change.hasNode, 'cardinality':'one'},
      'hasNextManifestation' : {'pred':Change.hasNode, 'cardinality':'one'},
      'hasInst': {'pred':Change.hasNode, 'cardinality':'one'}
  }

# manifestFirst creates the FirstManifestation for a class
# object: the class the first manifestation is created of
# instant: time.DateTimeDescription of when the manifestation comes into existance

def manifestFirst(object, dtd, ns) :
    inst = object(namespace=ns) if ns else object()
    inst.is_a.append(Change.FirstManifestation)	# obj is instance of two classes
    inst.primaryType = object
    inst.existsAt = dtd
    inst.hasFirstManifestation  = inst
    inst.hasLastManifestation  = inst
    inst.hasNextManifestation = None
    return(inst)

def py2graphdbManifestFirst(object, dtd, ns) :
    inst = ManifestationNode()
    inst.nameSpace = ns if ns else None
    inst.hasInst = object(namespace=ns) if ns else object()
    inst.is_a = Change.FirstManifestation	# obj is instance of two classes
    inst.primaryType = object
    inst.existsAt = dtd
    inst.hasFirstManifestation  = inst.hasInst
    inst.hasLastManifestation  = inst.hasInst
    inst.hasNextManifestation = None
    return(inst)

def manifest(man, dtd, ns=None) :
    if not ns : ns = man.namespace
    inst = man.hasFirstManifestation.primaryType(namespace=ns)
    inst.is_a.append(Change.Manifestation)
    for t in man.is_a :
        if (t != man.hasFirstManifestation.primaryType) and (t != Change.FirstManifestation) :
            inst.is_a.append(t)

    # copy over property values
    prevMan = man.hasFirstManifestation.hasLastManifestation
    props = set(prevMan.get_properties()) - {Change.hasNextManifestation, Change.hasPreviousManifestation,
                Change.hasFirstManifestation, Change.hasLastManifestation, Change.precedesManifestation,
                Change.existsAt, Change.primaryType}


    # Manage links
    inst.hasFirstManifestation = man.hasFirstManifestation
    inst.hasPreviousManifestation = inst.hasFirstManifestation.hasLastManifestation
    inst.hasFirstManifestation.hasLastManifestation = inst
    inst.hasPreviousManifestation.hasNextManifestation = inst
    inst.existsAt = dtd
    return(inst)

def py2graphdbManifest(man, dtd, ns=None):
    if not ns: ns = man.nameSpace

    new_inst = ManifestationNode()
    new_inst.primaryType = ns
    new_inst.is_a = Change.Manifestation

    for t in man.is_a:
        if (t != man.hasFirstManifestation.primaryType) and (t != Change.FirstManifestation):
            new_inst.is_a = t

    # copy over property values
    prevMan = man.hasFirstManifestation.hasLastManifestation
    props = set(prevMan.has_inst.get_properties()) - {Change.hasNextManifestation, Change.hasPreviousManifestation,
                                             Change.hasFirstManifestation, Change.hasLastManifestation,
                                             Change.precedesManifestation,
                                             Change.existsAt, Change.primaryType}
    for prop in props:
        if prop[prevMan]:
            if owl.FunctionalProperty in prop.is_a:
                setattr(new_inst.has_inst, prop.name, prop[prevMan.has_inst][0])
            else:
                prop[new_inst.has_inst] = prop[prevMan.has_inst]

    # Manage links
    new_inst.hasFirstManifestation = man.hasFirstManifestation
    new_inst.hasPreviousManifestation = new_inst.hasFirstManifestation.hasLastManifestation
    new_inst.hasFirstManifestation.hasLastManifestation = new_inst
    new_inst.hasPreviousManifestation.hasNextManifestation = new_inst
    new_inst.existsAt = dtd
    return (new_inst)

"""
def manifest(object, ns, firstManifestation, dtd) :
    global Change, Time, owltime, xsd
    inst = object(namespace=ns)
    inst.previousManifestation = firstManifestation.lastManifestation
    firstManifestation.lastManifestation = inst
    inst.previousManifestation.nextManifestation = inst
    inst.existsAt = dtd
    return(inst)
"""

# returns the manifestation that existsAt the instant
def findManifestation(man, dtd) :
    if not man.hasFirstManifestation : return(man)		# return man if there is no first manifestation

    firstManifestation = man.hasFirstManifestation
    # check if DateTimeDescription is less than the first manifestation
    if otime.lessThan(dtd, firstManifestation.existsAt) :
        return(None)

    lastMan = firstManifestation
    nextMan = lastMan.hasNextManifestation

    while nextMan :
        if otime.lessThan(dtd, nextMan.existsAt) : return(lastMan)
        lastMan = nextMan
        nextMan = lastMan.hasNextManifestation

    return(lastMan)


def py2graphdbFindManifestation(man, dtd):
    if not man.hasFirstManifestation: return (man)  # return man if there is no first manifestation

    firstManifestation = man.hasFirstManifestation
    # check if DateTimeDescription is less than the first manifestation
    if otime.lessThan(dtd, firstManifestation.existsAt):
        return (None)

    lastMan = firstManifestation
    nextMan = lastMan.hasNextManifestation

    while nextMan:
        if otime.lessThan(dtd, nextMan.existsAt): return (lastMan)
        lastMan = nextMan
        nextMan = lastMan.hasNextManifestation

    return (lastMan)


class TestPy2GraphDBFunctions(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.Change = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Change.owl').load()
		cls.Resource = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Resource.owl').load()
		cls.I72 = get_ontology('http://ontology.eil.utoronto.ca/5087/1/iso21972.owl').load()
		cls.Time = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Time.owl').load()

	def setUp(self):
		self.dtd = datetime.now()
		self.ns = "test_namespace"

	def test_py2graphdbManifestFirst(self):
		obj = self.Change.Manifestation
		inst = py2graphdbManifestFirst(obj, self.dtd, self.ns)

		self.assertEqual(inst.nameSpace, self.ns)
		self.assertEqual(inst.existsAt, self.dtd)
		self.assertEqual(inst.primaryType, obj)
		self.assertIs(inst.hasFirstManifestation, inst.hasInst)
		self.assertIs(inst.hasLastManifestation, inst.hasInst)
		self.assertIsNone(inst.hasNextManifestation)

	def test_py2graphdbManifest(self):
		obj = self.Change.Manifestation
		first_inst = py2graphdbManifestFirst(obj, self.dtd, self.ns)

		new_inst = py2graphdbManifest(first_inst, self.dtd, self.ns)

		self.assertEqual(new_inst.primaryType, self.ns)
		self.assertEqual(new_inst.existsAt, self.dtd)
		self.assertIs(new_inst.hasFirstManifestation, first_inst.hasInst)
		self.assertIs(new_inst.hasPreviousManifestation, first_inst.hasInst)
		self.assertIs(new_inst.hasFirstManifestation.hasLastManifestation, new_inst)
		self.assertIs(new_inst.hasPreviousManifestation.hasNextManifestation, new_inst)

	def test_py2graphdbFindManifestation(self):
		obj = self.Change.Manifestation
		first_inst = py2graphdbManifestFirst(obj, self.dtd, self.ns)
		new_inst = py2graphdbManifest(first_inst, self.dtd, self.ns)

		found_inst = py2graphdbFindManifestation(first_inst, self.dtd)

		# Check if the correct manifestation is found
		self.assertIs(found_inst, new_inst.hasFirstManifestation.hasLastManifestation)

if __name__ == '__main__':
	unittest.main()