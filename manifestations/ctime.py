"""
COTIME Module

Creator: Mark Fox
Version: 0.3
Date: 2 February 2021
License: Creative Commons

The CTIME module provides OWLReady2-based functions for manipulating an extension of 
the OWL-Time Ontology (https://www.w3.org/TR/owl-time/). CTIME extends OWL-Time by
defining the hasBeginning and hasEnd of a CDateTimeInterval as DateTimeInterval. 
This provides an interval of possible values (i.e., min and max) for the beginning and
end times of a DateTimeInterval. This allows for the specification of flexibility 
in the specification of the start and end times of an interval.  
CDurationDescription also extends the representation of DateTimeDuration to an interval of
possible duration values

TODOs:
1. Add duration calculation to temporal arc consistency

"""

import logging
from owlready2 import *
import datetime
import otime
from Utility import plog

ctime = get_namespace('http://ontology.eil.utoronto.ca/tove/ctime')
owltime = get_namespace('http://www.w3.org/2006/time')
time = get_namespace('http://ontology.eil.utoronto.ca/5087/Time/')
global dnet
dnet = None
bug = True

"""
"""
class DNetwork :
	"""
	Dnetwork is the main class for dependency network maintenance. It is designed to sit on
	top of a temporal network, in this case OWL-TIME's representation of DateTimeIntervals
	and DateTimeDescriptions, as extended by constrained time, defined in this module.

	The dependency keeps a linked list of changes to DateTimeDescriptions, and the source of
	the change, e.g., assertion or the temporal relation that caused the change. It enables
	the undoing of assertions and the inferences derived from them.
	"""

	def __init__(self, currentDnode=None, rootDnode=None) :
		self.currentDnode = currentDnode
		self.rootDnode = rootDnode
		self.nodeCount = 0
		
	def print(self) :
		print("Dependency Network Stack: ")
		cnode = self.rootDnode
		while cnode :
			print(cnode.nodeNumber, cnode.dtd.name, cnode.type, otime.printDTD(cnode.olddtd, prnt=False), "--->>", otime.printDTD(cnode.newdtd, prnt=False))
			cnode = cnode.nextDnode
	
	# undo "undos" assertions and inferences back to the dnodeNumber provided
	def undo(self, dnode=None) :
		cnode = self.currentDnode
		while cnode and cnode != dnode :
			oldcnode = cnode
			cnode = oldcnode.prevDnode
			oldcnode.undo()
			del oldcnode
			if not dnode : return
		if cnode == dnode : cnode.undo()

	def lastAssertion(self) :
		"""
		lastAssertion searches backwards from the last assertion/inference to the latest
		assertion made and returns its node number. To be used with the dependency network
		undo function.
		"""
	
		la = None
		cnode = self.rootDnode
		while cnode :
			if cnode.type == "assertion" : la = cnode
			cnode = cnode.nextDnode
		return(la)


class Dnode :
	def __init__(self, dtd=None, type="assertion", olddtd=None, newdtd=None, nextDnode=None, prevDnode=None) :
		global dnet
		self.dtd = dtd					# the dtd which is changed directly
		self.olddtd = olddtd			# the old value of dtd saved
		self.newdtd = newdtd			# the dtd that is copied into self.dtd by replaceWith
		self.nextDnode = nextDnode
		self.prevDnode= prevDnode
		self.type = type
		dnet.nodeCount += 1
		self.nodeNumber = dnet.nodeCount
	
	def print(self) :
		print("DNode #:", self.nodeNumber, " DTD Name: ", self.dtd.name, " Type: ", self.type, " DTD: ", otime.printDTD(self.dtd, prnt=False))
		
	def undo(self) :
		global dnet
		print("Undoing node # ", self.nodeNumber, " ", self.type, " ", otime.printDTD(self.dtd, prnt=False), " --->> ", otime.printDTD(self.olddtd))
		otime.copyDTD2DTD(self.olddtd, self.dtd)
		dnet.currentDnode = self.prevDnode
		if dnet.currentDnode : 
			dnet.nodeNumber = self.nodeNumber
			dnet.currentDnode.nextDnode = None
		else :
			dnet.rootDnode = None
			dnet.nodeCount = 0
		del self.olddtd
		del self.newdtd

# ------------------------------------------------------------------------------------
		
def printCDTI(cdti, prnt=True) :
	print(cdti.name, "-----------------")
	printCInstant(cdti.hasBeginning, prnt=True)
	printCInstant(cdti.hasEnd, prnt=True)
	
def printCInstant(cinst) :
	print("  ", cinst.name, ": ")
	print("    hasMin: ", cinst.hasMin.inDateTime.name, otime.printDTD(cinst.hasMin.inDateTime, prnt=False))
	print("    hasMax: ", cinst.hasMax.inDateTime.name, otime.printDTD(cinst.hasMax.inDateTime, prnt=False))

# createCDTI creates a CDateTimeInterval where all of the DateTimeDescriptions are set to zero
# note that 
def createCDTI(ns=None) :
	"""
	Instantiates a CDateTimeInterval and returns the instance. It instantiates the entire 
	pattern as depicted in Figure 1. Note: this function must be used to create a 
	constrained interval if dependency directed backtracking is to be use as it is necessary 
	that the instances of CInstant and Instant that be replaced, only the values of the 
	DateTimeDescription data properties can be changed.
	"""
	cdti = ctime.CDateTimeInterval(namespace=ns)
	cdti.hasBeginning = ctime.CInstant(namespace=ns)
	cdti.hasBeginning.hasMin = time.Instant(namespace=ns)
	cdti.hasBeginning.hasMin.inDateTime = time.DateTimeDescription(namespace=ns, year=0, month=0, day=0, hour=0, minute=0, second=0, unitType=owltime.unitSecond)
	cdti.hasBeginning.hasMax = time.Instant(namespace=ns)
	cdti.hasBeginning.hasMax.inDateTime = time.DateTimeDescription(namespace=ns, year=0, month=0, day=0, hour=0, minute=0, second=0, unitType=owltime.unitSecond)
	
	cdti.hasEnd = ctime.CInstant(namespace=ns)
	cdti.hasEnd.hasMin = time.Instant(namespace=ns)
	cdti.hasEnd.hasMin.inDateTime = time.DateTimeDescription(namespace=ns, year=0, month=0, day=0, hour=0, minute=0, second=0, unitType=owltime.unitSecond)
	cdti.hasEnd.hasMax = time.Instant(namespace=ns)
	cdti.hasEnd.hasMax.inDateTime = time.DateTimeDescription(namespace=ns, year=0, month=0, day=0, hour=0, minute=0, second=0, unitType=owltime.unitSecond)
	
	# add in the temporal relations
	cdti.hasBeginning.hasMin.before = [cdti.hasBeginning.hasMax]
	cdti.hasBeginning.hasMax.after = [cdti.hasBeginning.hasMin]
	cdti.hasEnd.hasMin.before = [cdti.hasEnd.hasMax]
	cdti.hasEnd.hasMax.after = [cdti.hasEnd.hasMin]
	return(cdti)

	
# replaces the first DTD values with the second DTD values
# maintains the dependency network of assertions and inferences
def replaceWith(dtd1, dtd2, ctype) :
	global dnet
#	pLog(bug, "replaceWith ", dtd1.name, " with ", dtd2.name)
	olddtd = otime.copyDTD(dtd1)
	dtd1.year = dtd2.year
	dtd1.month = dtd2.month
	dtd1.day = dtd2.day
	dtd1.hour = dtd2.hour
	dtd1.minute = dtd2.minute
	dtd1.second = dtd2.second
	dtd1.unitType = dtd2.unitType
	
	# record replacement in the dependency network
	dnode = Dnode(dtd=dtd1, olddtd=olddtd, newdtd=dtd2, type=ctype)
	dnode.prevDnode = dnet.currentDnode
	if not dnet.rootDnode : 
		dnet.rootDnode = dnode
	else :
		dnet.currentDnode.nextDnode = dnode
		dnode.prevDnode = dnet.currentDnode
	dnet.currentDnode = dnode
	
def cintervalConsistent(cint) :
	"""
	Determines whether an CDateTimeInterval is internally, temporally consistent, 
	i.e., if the hasBeginning min/max and hasEnd min/max are consistent
	1.	hasBeginning.hasMin <= hasBeginning .hasMax
	2.	hasEnd.hasMin <= hasEnd.hasMax
	3.	has.Beginning.hasMin <= hasEnd.hasMax

	"""
	# first check that each min/max are consistent
	if otime.greaterThan(cint.hasBeginning.hasMin.inDateTime, cint.hasBeginning.hasMax.inDateTime) : return(False)
	if otime.greaterThan(cint.hasEnd.hasMin.inDateTime, cint.hasEnd.hasMax.inDateTime) : return(False)
	if otime.greaterThan(cint.hasBeginning.hasMin.inDateTime, cint.hasEnd.hasMax.inDateTime) : return(False)
	return(True)


def intervalBeforeAC(cint1, cint2) :
	"""
	intervalBeforeAC(cint1, cint2) Updates the values of a Cint1 and  Cint2 based on 
	the intervalBefore temporal relation between cint1 acn cint2
	need to check if cint1 or cint2 are no longer consistent after the change
	
	Parameters
	----------
	cint1 : instance of CDateTimeInterval
	cint2 : instance of CDateTimeInterval
	
	Returns
	-------
	Set: of intervals that were changed by the temporal arc consistency (AC)
	"""
	if not (isinstance(cint1, ctime.CDateTimeInterval) and isinstance(cint2, ctime.CDateTimeInterval)) :
		pLog(bug, "intervalBeforeAC: not CDateTimeInterval")
		return(None)
	
	changedInts = set()
	
	otime.printDTD(cint1.hasEnd.hasMin.inDateTime, prnt=True)
	otime.printDTD(cint2.hasBeginning.hasMin.inDateTime, prnt=True)
	
	# If cint1.hasEnd.hasMin > cint2.hasBegining.hasMin then replaceWith cint2.hasBegining.hasMin with cint1.hasEnd.hasMin
	if otime.greaterThan(cint1.hasEnd.hasMin.inDateTime, cint2.hasBeginning.hasMin.inDateTime) :
		replaceWith(cint2.hasBeginning.hasMin.inDateTime, cint1.hasEnd.hasMin.inDateTime, "intervalBefore")
		changedInts.add(cint2)
		
	otime.printDTD(cint2.hasBeginning.hasMax.inDateTime, prnt=True)
	otime.printDTD(cint1.hasEnd.hasMax.inDateTime, prnt=True)
	
	# If Cinterval 2 Beg max < Cinterval 1 End max then set 1Emax to 2Bmax
	if otime.lessThan(cint2.hasBeginning.hasMax.inDateTime, cint1.hasEnd.hasMax.inDateTime) :
		replaceWith(cint1.hasEnd.hasMax.inDateTime, cint2.hasBeginning.hasMax.inDateTime, "intervalBefore")
		changedInts.add(cint1)
	
	return(changedInts)

def intervalAfterAC(cint1, cint2) :
	if not (isinstance(cint1, ctime.CDateTimeInterval) and isinstance(cint2, ctime.CDateTimeInterval)) :
		pLog(bug, "intervalAfterAC: not CDateTimeInterval")
		return(None)
	return(intervalBeforeAC(cint2, cint1, ns=ns))
	
		
def intervalOverlapsAC(cint1, cint2, ns=None) :
	if not (isinstance(cint1, ctime.CDateTimeInterval) and isinstance(cint2, ctime.CDateTimeInterval)) :
		pLog(bug, "intervalOverlapsAC: not CDateTimeInterval")
		return(None)
		
	changedInts = set()
	
	# If i1Emin < i2Bmin then set i1Emin = i2Bmin
	if otime.lessThan(cint1.hasEnd.hasMin.inDateTime, cint2.hasBeginning.hasMin.inDateTime) :
		replaceWith(cint1.hasEnd.hasMin.inDateTime, cint2.hasBeginning.hasMin.inDateTime, "intervalOverlaps")
		changedInts.add(cint1)
		
	# if i1Emin > i2Bmin then i2Bmin = i1Emin
	if otime.greaterThan(cint1.hasEnd.hasMin.inDateTime, cint2.hasBeginning.hasMin.inDateTime) :
		replaceWith(cint2.hasBeginning.hasMin.inDateTime, cint1.hasEnd.hasMin.inDateTime, "intervalOverlaps")
		changedInts.add(cint2)
		
	return(changedInts)
	
def intervalOverlappedByAC(cint1, cint2) :
	if not (isinstance(cint1, ctime.CDateTimeInterval) and isinstance(cint2, ctime.CDateTimeInterval)) :
		pLog(bug, "intervalOverlappedByAC: not CDateTimeInterval")
		return(None)
	return(intervalOverlapsAC(cint2, cint1, ns=ns))
	
		
def intervalContainsAC(cint1, cint2) :
	if not (isinstance(cint1, ctime.CDateTimeInterval) and isinstance(cint2, ctime.CDateTimeInterval)) :
		pLog(bug, "intervalContainsAC: not CDateTimeInterval")
		return(None)
		
	changedInts = set()
	
	# If i2Bmin < i1Bmin then set i2Bmin to i1Bmin
	if otime.lessThan(cint2.hasBeginning.hasMin.inDateTime, cint1.hasBeginning.hasMin.inDateTime) :
		replaceWith(cint2.hasBeginning.hasMin.inDateTime, cint1.hasBeginning.hasMin.inDateTime, "intervalContains")
		changedInts.add(cint2)
		
	# If i2Emax > i1Emax then set i2Emax to i1Emax
	if otime.greaterThan(cint2.hasEnd.hasMax.inDateTime, cint1.hasEnd.hasMax.inDateTime) :
		replaceWith(cint2.hasEnd.hasMax.inDateTime, cint1.hasEnd.hasMax.inDateTime, "intervalContains")
		changedInts.add(cint2)
		
	return(changedInts)
	
def intervalDuringAC(cint1, cint2) :
	if not (isinstance(cint1, ctime.CDateTimeInterval) and isinstance(cint2, ctime.CDateTimeInterval)) :
		pLog(bug, "intervalDuringAC: not CDateTimeInterval")
		return(None)
	return(intervalContainsAC(cint2, cint1, ns=ns))
	
def cIntervalAC(cint) :
	"""
	Checks to see if the interval is internally consistent. If the interval hasBeginning 
	min/max and hasEnd min/max are consistent wrt cint.hasBeginning being before cint.hasEnd. 
	It adjusts the values according to the following:
	1.	IF cint.hasBeginning.hasMax > cint.hasEnd.hasMax 
	    THEN replaceWith cint.hasBeginning.hasMax with cint.hasEnd.hasMax
	2.	IF cint.hasEnd.hasMin < cint.hasBeginning.hasMin 
	    THEN replaceWith cint.hasEnd.hasMin with cint.hasBeginning.hasMin
	"""
	if not isinstance(cint, ctime.CDateTimeInterval) :
		pLog(bug, "cItervalAC: not CDateTimeInterval")
		return(None)
		
	changedInts = set()
	
	if otime.greaterThan(cint.hasBeginning.hasMax.inDateTime, cint.hasEnd.hasMax.inDateTime) :
		replaceWith(cint.hasBeginning.hasMax.inDateTime, cint.hasEnd.hasMax.inDateTime, "cIntervalAC")
		# pLog(bug, "cintervalAC changed ", cint.hasBeginning.hasMax.inDateTime.name)
		changedInts.add(cint)
		
	if otime.lessThan(cint.hasEnd.hasMin.inDateTime, cint.hasBeginning.hasMin.inDateTime) :
		replaceWith(cint.hasEnd.hasMin.inDateTime, cint.hasBeginning.hasMin.inDateTime, "cIntervalAC")
		# pLog(bug, "cintervalAC changed ", cint.hasEnd.hasMin.inDateTime.name)
		changedInts.add(cint)
	
	return(changedInts)
	
# ------------------------------- Arc Consistency Main Functions --------------------------

def TAC_Graph(changedInterval) :
	"""
	TAC_Graph perform constrained temporal arc consistency starting at single changed
	CDTInterval, or over all of the CDTIntervals in the graph g.
	
	PARAMETERS
	----------
	changedInterval: single CDTInterval in graph that has changed
	
	RETURNS
	-------
	inconsistency: the CDTInterval or CDTInstant that is the source of the inconsistency.
	if it is None, then TAC completed with no inconsistencies
	"""
	

	# If single interval has changed then start there, else
	# initialize arc consistency changedIntervals to all intervals in the graph
	
	pLog(bug, '\n\n================ Starting TAC_Graph ==================')
	if changedInterval : 
		changedIntervals = {changedInterval}
	else : 
		changedIntervals = set(ns.search(type=ctime.CDateTimeInterval))
	
	while len(changedIntervals) > 0 :
		cint = changedIntervals.pop()
		pLog(bug, 'TAC_Graph:\n\tPerforming AC on ', cint.name)
		
		# check if interval is consistent
		if not cintervalConsistent(cint) :
			pLog(bug, "TAC_Graph inconsistent cinterval: ", cint.name)
			return(cint)
		
		# do intra CDTInterval arc consistency
		changedIntervals |= cIntervalAC(cint)
		
		# check if interval is consistent, again
		if not cintervalConsistent(cint) :
			pLog(bug, "TAC_Graph inconsistent cinterval: ", cint.name)
			return(cint)
	
		# perform temporal relation arc consistency for CDateTimeInterval
		for rint in cint.intervalBefore: 
			for changedInt in intervalBeforeAC(cint, rint) :
				if cintervalConsistent(changedInt) :
					changedIntervals.add(changedInt)
				else :
					pLog(bug, "TAC_Graph inconsistent cinterval: ", changedInt.name)
					return(changedInt)
		for rint in cint.intervalAfter: 
			for changedInt in intervalAfterAC(cint, rint) :
				if cintervalConsistent(changedInt) :
					changedIntervals.add(changedInt)
				else :
					pLog(bug, "TAC_Graph inconsistent cinterval: ", changedInt.name)
					return(changedInt)
		for rint in cint.intervalOverlaps: 
			for changedInt in intervalOverlapsAC(cint, rint) :
				if cintervalConsistent(changedInt) :
					changedIntervals.add(changedInt)
				else :
					pLog(bug, "TAC_Graph inconsistent cinterval: ", changedInt.name)
					return(changedInt)
		for rint in cint.intervalOverlappedBy:
			for changedInt in intervalOverlappedByAC(cint, rint) :
				if cintervalConsistent(changedInt) :
					changedIntervals.add(changedInt)
				else :
					pLog(bug, "TAC_Graph inconsistent cinterval: ", changedInt.name)
					return(changedInt)
		for rint in cint.intervalContains: 
			for changedInt in intervalContainsAC(cint, rint) :
				if cintervalConsistent(changedInt) :
					changedIntervals.add(changedInt)
				else :
					pLog(bug, "TAC_Graph inconsistent cinterval: ", changedInt.name)
					return(changedInt)
		for rint in cint.intervalDuring: 
			for changedInt in intervalDuringAC(cint, rint) :
				if cintervalConsistent(changedInt) :
					changedIntervals.add(changedInt)
				else :
					pLog(bug, "TAC_Graph inconsistent cinterval: ", changedInt.name)
					return(changedInt)
		
	return(None)
	
