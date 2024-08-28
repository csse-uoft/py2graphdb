"""
TOVE Constraint Module

Creator: Mark Fox
Version: 0.1
Date: 9 February 2021
License: Creative Commons

The TOVE Constraint module provides OWLReady2-based functions for finding instances that
match a set of constraints.

http://ontology.eil.utoronto.ca/5087/Change.owl


"""
from owlready2 import *
from utils import pLog
import otime

def satisfies(inst, constraints) :
	"""
	satisfies returns True if an instance satisfies a set of property constraints.
	Only works with functional properties at this time

	Parameters
	----------
	inst: instance
	objectConstraints: list of triples (property, predicate, value)
			object property predicates: "eq", "type"
	dataConstraints: list of triples (property, predicate, value)
			data property predicates: "lt", "gt", "le", "ge", "eq"
	"""

	props = inst.get_properties()
	print("props: ", props)
	for prop, pred, val in constraints :
		print(prop, prop.name, pred, val)
		if not prop in props : return(False)	# constrained prop not found
		pval = getattr(inst, prop.name)
		print("prop val: ", pval)
		if pred == "lt" : 
			if not pval < val : return(False)
		elif pred == "gt" :
			if not pval > val : return(False)
		elif pred == "le" :
			if not pval <= val : return(False)
		elif pred == "ge" :
			if not pval >= val : return(False)
		elif pred == "eq" :
			if not pval == val : return(False)
		elif pred == "type" :
			if not type(pval) == val : return(False)
	return(True)
		
def relatedAll(obj, prop, maxIterations=10000) :
	"""
		relatedAll finds all objects related to object via the property prop
		It uses both the basic DL properties of transitivity, etc. plus property chains
	
		Parameters
		----------
		obj : 	owl:Thing
					starting object for finding what is related to it by prop
		prop	:	owl:objectPropertyThing
					the property used to find what is related to the object
		
		Returns
		-------
					List of objects related to obj via prop
	"""	
	
	# get the list of property chains for prop
	propertyChains = prop.get_property_chain()
	
	currentObjects = {obj}
	relatedObjects = set()
	iteration = 0
	
	while (len(currentObjects) > 0) and (iteration < maxIterations) : 
		iteration += 1
		cObject = currentObjects.pop()
		relatedObjects = relatedObjects | {cObject}
		newObjects = prop[cObject].indirect()
		if newObjects : currentObjects = currentObjects | (set(newObjects) - relatedObjects)
	
		# process property chains
		for propertyChain in propertyChains :
			stageSet = {cObject}
			for chainProp in propertyChain.properties :
				newObjects = set()
				while (len(stageSet) > 0) and (iteration < maxIterations) :
					iteration += 1
					cobj = stageSet.pop()
					nobjects = set(chainProp[cobj].indirect())
					if cobj in nobjects : nobjects.remove(cobj)
					if nobjects : newObjects = newObjects | nobjects
				stageSet = newObjects
			currentObjects = currentObjects | (stageSet - relatedObjects)
	return(relatedObjects - {obj})

	
def related(obj1, prop, obj2, maxIterations=10000) :
	"""
		related determines whether obj1 is directly or indirectly connected to obj2
		using basic DL properties such as transitivity, inverse plus property chains
	
		Parameters
		----------
		obj1, obj2 : 	owl:Thing
					starting and ending objects for finding what is related to it by prop
		prop	:	owl:objectPropertyThing
					the property used to find what is related to the object
		
		Returns
		-------
					Boolean
	"""	
	return(obj2 in relatedAll(obj1, prop, maxIterations=maxIterations))
		
def relatedConstrained(inst, prop, constraints, dtd=None ) :
	# get all prop related instances
	relatedInst = constraint.relateAll(inst, prop)
	
	# filter manifestations by dtd if provided
	if dtd : 
		timeFiltered = set()
		for inst in relatedInst :
			timeFiltered.add(change.findManifestation())
		relatedInst = timeFiltered
	
	# filter using constraint
	constraintFilered = set()
	for inst in relatedInst :
		if constraint.satisfies(inst, constraints) : constraintFiltered.add(inst)

