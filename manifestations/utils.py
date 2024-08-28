"""
5087 Utility Module

Creator: Mark Fox
Version: 0.1
Date: 11 February 2021
License: Creative Commons

"""
import logging

def pLog(prin, *arg) :
	"""
	Log arguments and print to console (if specified).

	Parameters
	----------
	prin : bool
		Specifies if arguments should be printed to console.
	*arg : iterable object
		Variable number of arguments to be logged (and printed).
	"""
	pline = ""
	for a in arg : pline += str(a)
	if prin : print(pline)
	logging.info(pline)
	
def openLog(logFile="5087.log", level=logging.DEBUG) :
	logging.basicConfig(filename=logFile, filemode='w', level=level)

def closeLog() :
	pass