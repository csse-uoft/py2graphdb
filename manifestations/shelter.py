"""
TOVE Shelter Module

Creator: Mark Fox
Version: 0.1
Date: 16 March 2021
License: Creative Commons

The TOVE Shelter module provides OWLReady2-based functions for analysing shelter data.

http://ontology.eil.utoronto.ca/tove/shelter.owl


"""
from owlready2 import *
from utils import pLog
import change
import constraint
import otime

# global variables
Shelter = get_ontology('http://ontology.eil.utoronto.ca/tove/dt/ontologies/Shelter.owl')
Change = get_ontology('http://ontology.eil.utoronto.ca/5087/change.owl')


# find capacity based on property chain and satisfies constraints

def getCapacity(inst, constraints=None, dtd=None, manifestationdtd=None) :
	# find all occupants in the instance
	occupants = constraint.relatedAll(inst, Shelter.hasOccupant)
	
	# filter occupants by manifestation date
	oldOccupants = occupants
	occupants = set()
	for occ in oldOccupants :
		if isinstance(occ, Change.Manifestation) and  occ.hasFirstManifestation :
			if manifestationdtd : 
				occ = change.findManifestation(occ, manifestationdtd)
				occupants.add(occ)
			else :
				occupants.add(occ)
		else :
			occupants.add(occ)
	
	# filter manifestations by dtd if not none
	if dtd : 
		dateFilteredOccupants = set()
		for occ in occupants :
			if occ.forTimeInterval and otime.containsInstant(occ.forTimeInterval, dtd) : dateFilteredOccupants.add(occ)
	else :
		dateFilteredOccupants = occupants
	
	# filter using constraints
	if constraints :
		constraintFilteredOccupants = set()
		for occ in dateFilteredOccupants :
			if constraint.satisfies(inst, constraints) : constraintFilteredOccupants.add(inst)
	else :
		constraintFilteredOccupants = dateFilteredOccupants
	
	return(len(constraintFilteredOccupants))
	
def reserveBed() :
	pass
	
def releaseBed() :
	pass
	
def test() :
	pLog(True, '------------------- shelter.py Test START -------------------------')
	
	Shelter.load()
	Change.load()
	errors = []

	ttest = get_ontology('http://test.com/test')
	
	# Room 1 beds and occupants
	r1 = Shelter.Room()

	o1 = Shelter.Occupant(namespace=ttest)
	o1.identifier = ["occupant 1"]
	o1.forTimeInterval = otime.createDTI(otime.createDTD("2021 March 1"), otime.createDTD("2021 March 31"))
	b1 = Shelter.Bed(namespace=ttest)
	b1.hasOccupant= [o1]
	b1.forRoom = r1

	o2 = Shelter.Occupant(namespace=ttest)
	o2.identifier = ["occupant 2"]
	o2.forTimeInterval = otime.createDTI(otime.createDTD("2021 March 1"), otime.createDTD("2021 March 31"))
	b2 = Shelter.Bed(namespace=ttest)
	b2.hasOccupant= [o2]
	b2.forRoom = r1

	r1.hasBed = [b1, b2]

	# Room 2 beds and occupants
	r2 = Shelter.Room(namespace=ttest)

	o3 = Shelter.Occupant(namespace=ttest)
	o3.identifier = ["occupant 3"]
	o3.forTimeInterval = otime.createDTI(otime.createDTD("2021 March 1"), otime.createDTD("2021 March 31"))
	b3 = Shelter.Bed(namespace=ttest)
	b3.hasOccupant= [o3]
	b3.forRoom = r2

	o4 = Shelter.Occupant(namespace=ttest)
	o4.identifier = ["occupant 4"]
	o4.forTimeInterval = otime.createDTI(otime.createDTD("2021 March 1"), otime.createDTD("2021 March 31"))
	b4 = Shelter.Bed(namespace=ttest)
	b4.hasOccupant= [o4]
	b4.forRoom = r2

	o5 = change.manifestFirst(Shelter.Occupant, otime.createDTD("2020 January 1"), ttest)
	o5.identifier = ["occupant 5"]
	o5.forTimeInterval = otime.createDTI(otime.createDTD("2021 March 1"), otime.createDTD("2021 March 31"))
	b5 = Shelter.Bed(namespace=ttest)
	b5.hasOccupant= [o5]
	b5.forRoom = r2
	
	o6 = change.manifest(o5, otime.createDTD("2020 February 1"), ttest)
	o6.identifier = ["occupant 5"]
	o6.forTimeInterval = otime.createDTI(otime.createDTD("2022 March 1"), otime.createDTD("2022 March 31"))
	b5.hasOccupant= [o5, o6]

	r2.hasBed = [b3, b4, b5]

	b1 = Shelter.ShelterBuilding(namespace=ttest)
	b1.hasRoom = [r1, r2]
	s1 = Shelter.Shelter(namespace=ttest)
	Shelter.hasBuilding[s1] = [b1]
	
	dtd = otime.createDTD("2021 March 15")
	mdtd = otime.createDTD("2020 February 15")
	if getCapacity(s1, None, dtd, mdtd) == 4 :
		pLog(True, "  Capacity passed")
	else :
		pLog(True, "  Capacity FAILED")
		errors.append(("shelter", "E1"))
		
	dtd = otime.createDTD("2021 April 15")
	if getCapacity(s1, None, dtd) == 0 :
		pLog(True, "  Capacity outside of time interval passed")
	else :
		pLog(True, "  Capacity outside of time interval passed FAILED")
		errors.append(("shelter", "E2"))
	
	pLog(True, '------------------- shelter.py Test END -------------------------')
	return(errors)
