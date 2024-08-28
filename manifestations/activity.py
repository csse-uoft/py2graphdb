"""
TOVE Activity Module

Creator: Mark Fox
Version: 0.1
Date: 9 February 2021
License: Creative Commons

The TOVE Activity module provides OWLReady2-based functions for manipulating Manifestations
of Activites and States based on the activity ontology defined in:


Sathi A., M.S. Fox, M. Greenberg, (1985), “Representation of Activity Knowledge for Project Management”, 
IEEE Transactions on Pattern Analysis and Machine Intelligence, Vol. PAMI-7, No. 5, September, 1985, pp. 531- 552.

Gruninger, M., and Fox, M.S. , (1994), “An Activity Ontology for Enterprise Modelling”, 
Submitted to: Workshop on Enabling Technologies – Infrastructures for Collaborative Enterprises , West Virginia University.

"""
from owlready2 import *
from utils import pLog
import otime
import change
import resource

global Change, Time, owltime, xsd
Change = get_ontology('http://ontology.eil.utoronto.ca/5087/Change.owl').load()
Time = get_ontology('http://ontology.eil.utoronto.ca/5087/Time.owl')
Resource = get_ontology('http://ontology.eil.utoronto.ca/5087/Resource.owl')
owltime = get_namespace('http://www.w3.org/2006/time')
xsd = get_namespace('http://www.w3.org/2001/XMLSchema')


"""
assignResource assigns a designated resource to a state for a particular time interval.
It creates a new manifestation of both the resource and state to contain the change
in their properties.

Parameters
----------
res :	manifestation of resource to be assigned
state : manifestation of state to be assigned
ti :	time interval of the assignment

Returns
-------
(resourceMan, stateMan)
		newRes is the new manifestation of the provided resource
		newState is the new manifestation of the provided state
"""

def assignResource(res, state, dtd, cap=1.0) :
	newState = change.manifest(state, otime.copyDTD(dtd))
	newResource = change.manifest(res, otime.copyDTD(dtd))
	newState.hasResource = [newResource]
	newResource.allocatedCapacity.append(newState)
	


def test()
	errors = []
	return(errors)