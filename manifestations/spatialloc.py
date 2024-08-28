"""
Spatial Loc functions for 5087

Creator: Paul Xie, Mark Fox
Date: 5 February 2021
License: Creative Commons

This module takes as input/output a wktLiteral which is the value of the property geo:asWKT. 

Example:

"POLYGON((-77.050125 38.892086, -77.039482 38.892036, -77.039482 38.895393, -77.033669 38.895508, 
	-77.033585 38.892052, -77.031906 38.892086, -77.031883 38.887474, -77.050232 38.887142, 
	-77.050125 38.892086 ))"
	
New functions to add:
1. Distance between two points.
2. 

"""

from owlready2 import *
import pandas as pd
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
import shapely
from shapely.geometry import Polygon, LineString, Point
from utils import pLog

# global variables
geo = get_namespace("http://www.opengis.net/ont/geosparql")
Spatialloc = get_ontology("http://ontology.eil.utoronto.ca/5087/SpatialLoc.owl")

## a function that maps a given lat/long pair to specific address
def latLongAddress(pointWKT, locator=Nominatim(user_agent='myGeocoder')):
	poi = shapely.wkt.loads(pointWKT)
	location = locator.reverse([poi.x, poi.y])
	return(location[0])


## a function that maps a given address to a pair of lat/long
def addressLatLong(address, locator=Nominatim(user_agent='myGeocoder')):
    location = locator.geocode(address)
    poi = Point([location.latitude, location.longitude])
    return(poi.wkt)


## given lat/long and a shape file (Polygon), return whether the location 
## is within the shape file. The parameter shape can also be a list of tuples,
## with each tuple being a pair of lat/long

def locationInside(pointWKT, polygonWKT):
	poi = shapely.wkt.loads(pointWKT)
	poly = shapely.wkt.loads(polygonWKT)
	return(poi.within(poly))


## a function that returns the spatial relation of two shape files,
## the inputs can also be two lists of tuples, with each tuple being 
## a pair of lat/long. 
def spatialRelation(geoWKT1, geoWKT2):
	shape_1 = shapely.wkt.loads(geoWKT1)
	shape_2 = shapely.wkt.loads(geoWKT2)
	
#	if type(shape_1) != Polygon: shape_1 = Polygon(shape_1)
#	if type(shape_2) != Polygon: shape_2 = Polygon(shape_2)
	
	if shape_1.equals(shape_2):
		return(geo.sfEquals)
	elif shape_1.touches(shape_2):
		return(geo.sfTouches)
	elif shape_1.within(shape_2):
		return(geo.sfWithin)
	elif shape_1.contains(shape_2):
		return(geo.sfContains)
	elif shape_1.disjoint(shape_2):
		return(geo.sfDisjoint)
	elif shape_1.crosses(shape_2):
		return(geo.sfCrosses)
	elif shape_1.intersects(shape_2):
		return(geo.sfIntersects)
	elif shape_1.overlaps(shape_2):
		return(geo.sfOverlaps)
	
	return(None)

# returns the distance between to long/lat points
def distance(geoWKT1, geoWKT2) :
	shape_1 = shapely.wkt.loads(geoWKT1)
	shape_2 = shapely.wkt.loads(geoWKT2)
	dist = shape_1.distance(shape_2)
	return(dist)
	
# test code for resource
def test() :
	Spatialloc.load()
	errors = []
	pLog(True, '------------------- spatialloc.py Test START -------------------------')

	testArea = 'POLYGON((-1 -1, -1 1, 1 1, 1 -1, -1 -1))'

	asWKT = "POINT(0 0)"
	
	if spatialRelation(asWKT, testArea) == geo.sfWithin :
		pLog(True, "  point in polygon passed")
	else :
		pLog(True, "  point in polygon FAILED")
		errors.append(("spatialloc", "E1"))
	
	# outside of polygon
	asWKT = "POINT(3 -2)"
	
	if spatialRelation(asWKT, testArea) == geo.sfDisjoint :
		pLog(True, "  point outside polygon passed")
	else :
		pLog(True, "  point outside polygon FAILED")
		errors.append(("spatialloc", "E2"))
	
	# test polygon inside of polygon
	asWKT = "POLYGON((-0.5 -0.5, 0.5 0, 0.5 -0.5, -0.5 -0.5))"
	
	if spatialRelation(asWKT, testArea) == geo.sfWithin :
		pLog(True, "  polygon inside polygon passed")
	else :
		pLog(True, "  polygon inside polygon passed FAILED")
		errors.append(("spatialloc", "E3"))

	
	pLog(True, '------------------- spatialloc.py Test START -------------------------')
	return(errors)

