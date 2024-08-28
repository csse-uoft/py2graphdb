"""
cityagent module provides functions for the operation of the CityAgent

"""

# Activity actions
# 1. Add/remove an Activity
# 2. Add/Remove a Temporal Interval to an activity
# 3. Add/Remove a start/end temporal instant
# 4. Add/Remove bounds on temporal instant
# 5. Add/Remove resource (disjunct/conjunct)

# Distinguish between inferred versus asserted values

- Activity rep with resources
- Add temporal constraint between two activities
- propagate

Add temporal constraint to two activities
 - each activity has a temporal interval, arc consistency occurs
 - new interval generated: status of proposed, caused by constraint
   - each resource is asked if it can still satisfy constraint
   - each resource returns available interval
   - max start time and min end time selected as revised interval
     - resources updated with new time
     - activity is updated with new time
     
Programming approach
  - activity, state and resources are classes with functions performing tasks
  - underlying representation is rdflib

# ----------------------------------------------------------------------------------------
#			Functions for adding activity constraints
# ----------------------------------------------------------------------------------------

def actAddactBefore(act1, act2, agent) :
	# create a constraint with actBefore as the property constraint
	# set constraint to asserted
	# set source of constraint to agent
	
	# add equivalent temporal relations to each activity as a constraint and set
	# set source to the actBefore constraint
	

	# 

def actRemConstraint(cons) :