"""
TIME Module

Creator: Mark Fox
Version: 0.3
Date: 2 February 2021
License: Creative Commons

The OTIME module provide OWLReady2-based functions for manipulating OWL-TIME classes and
properties.

"""

from owlready2 import *
import datetime
from utils import pLog
from dateutil import parser

# global variables
owltime = get_namespace('http://www.w3.org/2006/time')
Time = get_ontology('http://ontology.eil.utoronto.ca/5087/Time.owl')

def createDTD(dts, ns=None) :
	dt = parser.parse(dts)
	newdtd = Time.DateTimeDescription(namespace=ns)
	newdtd.year = dt.year
	newdtd.month = dt.month
	newdtd.day = dt.day
	newdtd.hour = dt.hour
	newdtd.minute = dt.minute
	newdtd.second = dt.second
	newdtd.unitType = owltime.unitSecond
	return(newdtd)
	
def printDTD(dtd, prnt=True) :
	text = str(dtd.year) + "-" + str(dtd.month) + "-" + str(dtd.day) + "T" + str(dtd.hour) + ":" + str(dtd.minute) + ":" + str(dtd.second)
	if prnt : pLog(True, dtd.name, ": ", text)
	return(text)

def copyDTD(dtd, ns=None) :
	newdtd = Time.DateTimeDescription(namespace=ns)
	newdtd.year = dtd.year
	newdtd.month = dtd.month
	newdtd.day = dtd.day
	newdtd.hour = dtd.hour
	newdtd.minute = dtd.minute
	newdtd.second = dtd.second
	newdtd.unitType = dtd.unitType
	return(newdtd)

# copies dtd1 into dtd2
def copyDTD2DTD(dtd1, dtd2) :
	dtd2.year = dtd1.year
	dtd2.month = dtd1.month
	dtd2.day = dtd1.day
	dtd2.hour = dtd1.hour
	dtd2.minute = dtd1.minute
	dtd2.second = dtd1.second
	dtd2.unitType = dtd1.unitType

# create a datetime interval
def createDTI(bdtd, edtd, ns=None) :
	binst = Time.Instant(namespace=ns, inDateTime = bdtd)
	einst = Time.Instant(namespace=ns, inDateTime = edtd)
	interv = owltime.DateTimeInterval(namespace=ns)
	interv.hasBeginning = binst
	interv.hasEnd = einst
	return(interv)
	
def printDTI(dti) :
	print("Interval: ", dti.name)
	print("  hasBeginning: ", printDTD(dti.hasBeginning.inDateTime, prnt=False))
	print("  hasEnd: ", printDTD(dti.hasEnd.inDateTime, prnt=False))

# Adds duration to DTD and returns a new DTD containing the result
# it uses datetime package to do the subtraction of time properly
def addDTD(dtd, dur, ns=None) :
	dt = datetime.datetime(dtd.year, dtd.month, dtd.day, dtd.hour, dtd.minute, dtd.second)
	dt = dt + datetime.timedelta(days=dur.days, hours=dur.hours, minutes=dur.minutes, seconds=dur.seconds)
	m = dt.month + dur.months
	newMonth = m % 12
	newYear = dt.year + (m // 12) + dur.years
	return(Time.DateTimeDescription(namespace=ns, year = newYear, month = newMonth, day = dt.day, hour = dt.hour, minute = dt.minute, second = dt.second, unitType = dtd.unitType))
	
# subtracts duration from DTD and returns a new DTD containing the result
# it uses datetime package to do the subtraction of time properly
def subtractDTD(dtd, dur, ns=None) :
	dt = datetime.datetime(dtd.year, dtd.month, dtd.day, dtd.hour, dtd.minute, dtd.second)
	dt = dt - datetime.timedelta(days=dur.days, hours=dur.hours, minutes=dur.minutes, seconds=dur.seconds)
	m = dt.month - dur.months
	newMonth = m if m > 0 else 12 - (abs(m) % 12)
	newYear = dt.year - dur.years
	if m <= 0 : newYear = newYear - (abs(m) // 12)
	return(Time.DateTimeDescription(namespace=ns, year = newYear, month = newMonth, day = dt.day, hour = dt.hour, minute = dt.minute, second = dt.second, unitType = dtd.unitType))
	
# determines if dtd1 is less than dtd2
def lessThan(dtd1, dtd2) :
	if dtd1.year < dtd2.year : return(True)		
	if (dtd1.year > dtd2.year) or ((dtd1.year == dtd2.year) and (dtd1.unitType == owltime.unitYear)) : return(False)
	if dtd1.month < dtd2.month : return(True)
	if (dtd1.month > dtd2.month) or ((dtd1.month == dtd2.month) and (dtd1.unitType == owltime.unitMonth)) : return(False)
	if dtd1.day < dtd2.day : return(True)
	if (dtd1.day > dtd2.day) or ((dtd1.day == dtd2.day) and (dtd1.unitType == owltime.unitDay)) : return(False)
	if dtd1.hour < dtd2.hour : return(True)
	if (dtd1.hour > dtd2.hour) or ((dtd1.hour == dtd2.hour) and (dtd1.unitType == owltime.unitHour)) : return(False)
	if dtd1.minute < dtd2.minute : return(True)
	if (dtd1.minute > dtd2.minute) or ((dtd1.minute == dtd2.minute) and (dtd1.unitType == owltime.unitMinute)) : return(False)
	if dtd1.second < dtd2.second : return(True)
	if (dtd1.second > dtd2.second) or ((dtd1.second == dtd2.second) and (dtd1.unitType == owltime.unitSecond)) : return(False)
	return(False)	# they are equal
	
# determines if dtd1 is greater than than dtd2
def greaterThan(dtd1, dtd2) :
	if dtd1.year > dtd2.year : return(True)		
	if (dtd1.year < dtd2.year) or ((dtd1.year == dtd2.year) and (dtd1.unitType == owltime.unitYear)) : return(False)
	if dtd1.month > dtd2.month : return(True)
	if (dtd1.month < dtd2.month) or ((dtd1.month == dtd2.month) and (dtd1.unitType == owltime.unitMonth)) : return(False)
	if dtd1.day > dtd2.day : return(True)
	if (dtd1.day < dtd2.day) or ((dtd1.day == dtd2.day) and (dtd1.unitType == owltime.unitDay)) : return(False)
	if dtd1.hour > dtd2.hour : return(True)
	if (dtd1.hour < dtd2.hour) or ((dtd1.hour == dtd2.hour) and (dtd1.unitType == owltime.unitHour)) : return(False)
	if dtd1.minute > dtd2.minute : return(True)
	if (dtd1.minute < dtd2.minute) or ((dtd1.minute == dtd2.minute) and (dtd1.unitType == owltime.unitMinute)) : return(False)
	if dtd1.second > dtd2.second : return(True)
	if (dtd1.second < dtd2.second) or ((dtd1.second == dtd2.second) and (dtd1.unitType == owltime.unitSecond)) : return(False)
	return(False)	# they are equal
	
# determines if dtd1 is equal to dtd2
def equal(dtd1, dtd2) :
	if dtd1.year != dtd2.year : return(False)		
	if dtd1.unitType == owltime.unitYear : return(True)

	if dtd1.month != dtd2.month : return(False)
	if dtd1.unitType == owltime.unitMonth : return(True)
	
	if dtd1.day != dtd2.day : return(False)
	if dtd1.unitType == owltime.unitDay : return(True)
	
	if dtd1.hour != dtd2.hour : return(False)
	if dtd1.unitType == owltime.unitHour : return(True)
	
	if dtd1.minute != dtd2.minute : return(False)
	if dtd1.unitType == owltime.unitMinute : return(True)
	
	if dtd1.second != dtd2.second : return(False)
	
	return(True)	# they are equal
	
def intervalBefore(int1, int2) :
	return(lessThan(int1.hasEnd.inDateTime, int2.hasBeginning.inDateTime))
	
def intervalAfter(int1, int2) :
	return(lessThan(int2.hasEnd.inDateTime, int1.hasBeginning.inDateTime))
	
def intervalDuring(int1, int2) :
	return(greaterThan(int1.hasBeginning.inDateTime, int2.hasBeginning.inDateTime) and lessThan(int1.hasEnd.inDateTime, int2.hasEnd.inDateTime))
	
def intervalContains(int1, int2) :
	return(intervalDuring(int2, int1))

def intervalOverlaps(int1, int2) :
	return(lessThan(int1.hasBeginning.inDateTime, int2.hasBeginning.inDateTime) and greaterThan(int1.hasEnd.inDateTime, int2.hasBeginning.inDateTime) and (lessThan(int1.hasEnd.inDateTime, int2.hasEnd.inDateTime)))

def containsInstant(int, dtd) :
	return(not lessThan(dtd, int.hasBeginning.inDateTime, ) and not greaterThan(dtd, int.hasEnd.inDateTime))
	
# test code for otime.py
def test() :
	Time.load()
	
	pLog(True, '------------------- otime.py Test START -------------------------')
	ttest = get_ontology('http://test.org/test')
	errors = []
	
	dtd1 = Time.DateTimeDescription(namespace=ttest, year=2021, month=2, day=10, hour=1, minute=6, second=0, unitType=owltime.unitSecond)
	dtd2 = Time.DateTimeDescription(namespace=ttest, year=2021, month=2, day=10, hour=21, minute=15, second=0, unitType=owltime.unitSecond)
	dtd3 = Time.DateTimeDescription(namespace=ttest, year=2022, month=3, day=10, hour=22, minute=6, second=0, unitType=owltime.unitSecond)
	dtd4 = Time.DateTimeDescription(namespace=ttest, year=2023, month=3, day=10, hour=22, minute=6, second=0, unitType=owltime.unitSecond)
	dtd6 = Time.DateTimeDescription(namespace=ttest, year=2025, month=3, day=10, hour=22, minute=6, second=0, unitType=owltime.unitSecond)
	
	if lessThan(dtd1, dtd2) : 
		pLog(True, "  otime.lessThan passed")
	else :
		pLog("  otime.lessThan FAILED")
		errors.append(("otime", "E1"))
		
	if greaterThan(dtd2, dtd1) : 
		pLog(True, "  otime.greaterThan passed")
	else :
		pLog(True, "  otime.greaterThan FAILED")
		errors.append(("otime", "E2"))
		
	try :
		dtd4 = copyDTD(dtd3)
	except :
		pLog(True, "  ti.copyDTD FAILED")
		errors.append(("otime", "E3"))

	if equal(dtd1, dtd1) and not equal(dtd1, dtd2) :
		pLog(True, "  otime.equal passed")
	else :
		pLog(True, "  otime.equal FAILED")
		errors.append(("otime", "E4"))
		
	if not lessThan(dtd3, dtd4) and not greaterThan(dtd3, dtd4)  : 
		pLog(True, "  otime.copyDTD values passed")
	else :
		pLog(True, "  otime.copyDTD values FAILED")
		errors.append(("otime", "E5"))
		
	dur = Time.DurationDescription(namespace=ttest, years=1, months=1, days=0, hours=0, minutes=51, seconds=0, unitType=owltime.unitSeconds)
	dtd4 = addDTD(dtd2, dur, ns=ttest)
	
	if equal(dtd4, dtd3) :
		pLog(True, "  time.addDTD passed")
	else :
		pLog(True, "  time.addDTD FAILED")
		errors.append(("otime", "E6"))
		
	dtd5 = subtractDTD(dtd3, dur, ns=ttest)
	
	if equal(dtd2, dtd5) :
		pLog(True, "  time.subtractDTD passed")
	else :
		pLog(True, "  time.subtractDTD FAILED")
		errors.append(("otime", "E7"))
	
	int1 = createDTI(dtd1, dtd3, ns=ttest)
	if not containsInstant(int1, dtd6) :
		pLog(True, "  time.constainsInstant passed")
	else :
		pLog(True, "  time.constainsInstant FAILED")
		errors.append(("otime", "E8"))

	pLog(True, '------------------- otime.py Test END -------------------------')
	return(errors)