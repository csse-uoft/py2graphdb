"""
TOVE Resource Module

Creator: Mark Fox
Version: 0.3
Date: 9 February 2021
License: Creative Commons

The TOVE Resource module provides OWLReady2-based functions for manipulating resources
based on the resource ontology defined in ISO/IEC 5087.

These functions assume that a Resource is subclass of Manifestation, and that changes
to property values of a resource are made according to the Change ontology and best
done using the change.py functions.

The TOVE Traceable Resource module provides OWLReady2-based functions for tracing resources
based on the resource ontology defined in:
Kim, H.M., Fox, M.S., and Gruninger, M., (1999), “An ontology for quality management – 
enabling quality problem identification and tracing”, BT Technology Journal, 
Vol. 17, No. 4, pp. 131-140.
http://www.eil.utoronto.ca/wp-content/uploads/enterprise-modelling/papers/Kim-BT99v17n4.pdf

Tasks: What are the basic operations on a resource
1. capacity available at time t?
2. Consume a quantity of a resource - generates a new manifestation
3. Combine two or more resources - creates a new resource
4. relocate a resource - create a new manifestation

"""

from utils import pLog
from owlready2 import *
import shapely
import constraint
import spatialloc
import change
import otime


# global variables
Resource = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Resource.owl')
i72 = get_ontology("http://ontology.eil.utoronto.ca/5087/1/iso21972.owl")
SpatialLoc = get_ontology("http://ontology.eil.utoronto.ca/5087/1/SpatialLoc.owl")
Change = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Change/')
Time = get_ontology('http://ontology.eil.utoronto.ca/5087/1/Time.owl')
geo = get_namespace("http://www.opengis.net/ont/geosparql")



"""
"""

# determine capacity availability at time t
def resourceCapacityT(resType, dtd) :
	
	# find first Manifestations only as instances() will return all manifestations
	firstMans = set()
	for man in resType.instances() : firstMans.add(man.hasFirstManifestation)
	
	# find resource according to the time
	totalCapacity = 0.0
	for firstMan in  firstMans:
		resMan = change.findManifestation(firstMan, dtd)
		if resMan : totalCapacity += float(resMan.hasCapacity.value.numerical_value)
	return(totalCapacity) 

# determine capacity availability at time t and location loc
def resourceCapacityLT(resType, locWKT, dtd) :
	
	loc = shapely.wkt.loads(locWKT)
	
	# find first Manifestations only
	firstMans = set()
	for man in resType.instances() : firstMans.add(man.hasFirstManifestation)
	
	totalCapacity = 0.0
	for firstMan in firstMans :
		resMan = change.findManifestation(firstMan, dtd)

		if resMan and resMan.hasLocation and resMan.hasLocation.hasGeometry : 
			loc2 = shapely.wkt.loads(resMan.hasLocation.hasGeometry.asWKT)
			if loc.contains(loc2) or loc.equals(loc2) :
				totalCapacity += float(resMan.hasCapacity.value.numerical_value)
				
	return(totalCapacity)

# allocates a resource to a state and creates an Allocation specifying it
# Note that no knew manifestation of either the resource or state is made
# as the actual capacities go unchanged

def allocateResource(res, state, quant, ti, ns=None) :
	alloc = Resource.Allocation(namespace=ns)
	alloc.forResource = res
	alloc.forState = state
	alloc.hasTime = ti
	alloc.hasQuantity = quant
	res.hasAllocation.append(alloc)
	state.hasAllocation.append(alloc)
	return(alloc)

# updates capacities
def deleteAllocation(alloc) :
	#### update capacities
	pass



# test code for resource
def test() :
	Resource.load()
	SpatialLoc.load()
	i72.load()
	
	errors = []
	pLog(True, '------------------- resource.py Test START -------------------------')
	ttest = get_ontology('http://test.com/test')

	dtd1 = Time.DateTimeDescription(year=2021, month=2, day=10, hour=0, minute=6, second=0)
	dtd2 = Time.DateTimeDescription(year=2021, month=2, day=10, hour=10, minute=15, second=0)
	dtd3 = Time.DateTimeDescription(year=2021, month=2, day=10, hour=20, minute=6, second=0)

	with ttest :
		class Oil(Resource.Resource) :
			pass

	testArea = 'POLYGON((-1 -1, -1 1, 1 1, 1 -1, -1 -1))'
	
	# First oil  resource point 
	oil1 = change.manifestFirst(ttest.Oil, dtd1, ttest)
	oil1.hasCapacity = quant = i72.Quantity(namespace = ttest)
	quant.value = m = i72.Measure(namespace = ttest,numerical_value = "10")
	loc = SpatialLoc.Feature(namespace = ttest)
	oil1.hasLocation = loc
	loc.hasGeometry = geom = SpatialLoc.Geometry(namespace = ttest)
	geom.asWKT = "POINT(0 0)"
	
	# Second oil  resource point 
	oil2 = change.manifestFirst(ttest.Oil, dtd2, ttest)
	oil2.hasCapacity = quant = i72.Quantity(namespace = ttest)
	quant.value = i72.Measure(namespace = ttest, numerical_value="5")
	loc = SpatialLoc.Feature(namespace = ttest)
	oil2.hasLocation = loc
	loc.hasGeometry = geom = SpatialLoc.Geometry(namespace = ttest)
	geom.asWKT = "POINT(-0.5 0.5 )"
	
	# Third oil  resource point 
	oil3 = change.manifestFirst(ttest.Oil, dtd3, ttest)
	oil3.hasCapacity = quant = i72.Quantity(namespace = ttest)
	quant.value = i72.Measure(namespace = ttest, numerical_value="3")
	loc = SpatialLoc.Feature(namespace = ttest)
	oil3.hasLocation = loc
	loc.hasGeometry = geom = SpatialLoc.Geometry(namespace = ttest)
	geom.asWKT = "POINT(3 -2)"

	cap = resourceCapacityT(Resource.Resource, dtd1)
	if cap == 10 :
		print("  Resource Capacity 1 passed")
	else :
		print("  Resource Capacity 1 FAILED")
		errors.append(("resource", "E1"))
		
	cap = resourceCapacityT(Resource.Resource, dtd2)
	if cap == 15 :
		print("  Resource Capacity 2 passed")
	else :
		print("  Resource Capacity 2 FAILED")
		errors.append(("resource", "E2"))
		
	cap = resourceCapacityT(Resource.Resource, dtd3)
	if cap == 18 :
		print("  Resource Capacity 3 passed")
	else :
		print("  Resource Capacity 3 FAILED")
		errors.append(("resource", "E3"))
		
	cap = resourceCapacityLT(Resource.Resource, "POINT(0 0)", dtd1)
	if cap == 10 :
		print("  Resource Capacity Location 1 passed")
	else :
		print("  Resource Capacity Location 1 FAILED")
		errors.append(("resource", "E4"))
		
	cap = resourceCapacityLT(Resource.Resource, testArea, dtd3)
	if cap == 15 :
		print("  Resource Capacity Location 2 passed")
	else :
		print("  Resource Capacity Location 2 FAILED")
		errors.append(("resource", "E5"))
		
	cap = resourceCapacityLT(Resource.Resource, testArea, dtd3)
	if cap == 15 :
		print("  Resource Capacity Location 3 passed")
	else :
		print("  Resource Capacity Location 3 FAILED")
		errors.append(("resource", "E6"))
		
	
	pLog(True, '------------------- resource.py Test END -------------------------')
	return(errors)
	

# ISSUE: how can a resource be in more than one place at one time --> dealing with resource type