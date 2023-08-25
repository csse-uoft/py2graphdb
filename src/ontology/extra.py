from owlready2 import ObjectProperty, DataProperty, rdfs, Thing 

class hasTraceID(ObjectProperty):
    rdfs.comment = ["Trace this object belongs to."]
    range = [Thing]

class hasHypotheses(ObjectProperty):
    rdfs.comment = ["Hypothesis for this object."]
    range = [Thing]


class hasKSInstance(ObjectProperty):
    rdfs.comment = ["KS INstance for this object."]
    range = [Thing]

class hasCertainty(DataProperty):
    rdfs.comment = ["Certainty value for this object."]
    range = [float]

class hasRequest(ObjectProperty):
    rdfs.comment = ["Request for this object."]
    range = [Thing]


class hasHypotheses(ObjectProperty):
    rdfs.comment = ["Hypotheses for this object."]
    range = [Thing]

class hasRequests(ObjectProperty):
    rdfs.comment = ["Requets for this object."]
    range = [Thing]

class hasName(DataProperty):
    rdfs.comment = ["Name for this object."]
    range = [str]

class hasPyName(DataProperty):
    rdfs.comment = ["Python Name for this object."]
    range = [str]

class hasKSInstances(ObjectProperty):
    rdfs.comment = ["KS Instances for this object."]
    range = [Thing]

class hasGroupInputLevels(ObjectProperty):
    rdfs.comment = ["Group Input Levels for this object."]
    range = [Thing]

class hasInputDataType(ObjectProperty):
    rdfs.comment = ["Input Data Types for this object."]
    range = [Thing]

class hasOutputDataType(ObjectProperty):
    rdfs.comment = ["Output Data Types for this object."]
    range = [Thing]

class hasInputDataTypes(ObjectProperty):
    rdfs.comment = ["Input Data Types for this object."]
    range = [Thing]

class hasOutputDataTypes(ObjectProperty):
    rdfs.comment = ["Output Data Types for this object."]
    range = [Thing]


class hasKS(ObjectProperty):
    rdfs.comment = ["KS for this object."]
    range = [Thing]

class hasDataLevel(DataProperty):
    rdfs.comment = ["Data Type for this object."]
    range = [str]

class hasKSInstanceStatus(DataProperty):
    rdfs.comment = ["Status for this KS Instance object."]
    range = [int]

class hasKSObjectPicklePath(DataProperty):
    rdfs.comment = ["Holds pickle version of KnowledgeSource object for this KS Instance object."]
    range = [str]


class hasCoRefWord(ObjectProperty):
    rdfs.comment = ["Holds Word that acts as CoRef for Word object."]
    range = [Thing]

class hasRefWord(ObjectProperty):
    rdfs.comment = ["Holds Word that acts as main Word object."]
    range = [Thing]


class hasContent(DataProperty):
    rdfs.comment = ["Holds text content for an object."]
    range = [str]


class hasContentLabel(DataProperty):
    rdfs.comment = ["Holds token label for the text an object."]
    range = [str]

class hasStart(DataProperty):
    rdfs.comment = ["Holds start index of a token an object."]
    range = [int]
class hasEnd(DataProperty):
    rdfs.comment = ["Holds start index of a token an object."]
    range = [int]

class hasPhrases(ObjectProperty):
    rdfs.comment = ["Holds Word that acts as main Word object."]
    range = [Thing]

class hasPos(ObjectProperty):
    rdfs.comment = ["Holds part-of-speach label for main object."]
    range = [Thing]

class hasKsInput(ObjectProperty):
    rdfs.comment = ["Holds KsInput for main object."]
    range = [Thing]

class hasKsOutput(ObjectProperty):
    rdfs.comment = ["Holds KsOutput for main object."]
    range = [Thing]

class hasDepLabel(DataProperty):
    rdfs.comment = ["Holds dependency edge label for main object."]
    range = [str]

class hasSubjectWord(ObjectProperty):
    rdfs.comment = ["Holds Subject Word for main object."]
    range = [Thing]

class hasObjectWord(ObjectProperty):
    rdfs.comment = ["Holds Object Word for main object."]
    range = [Thing]

class hasPhrase(ObjectProperty):
    rdfs.comment = ["Holds Phrase for main object."]
    range = [Thing]

class hasEntity(ObjectProperty):
    rdfs.comment = ["Holds Entity type for main object."]
    range = [str]

class hasWords(ObjectProperty):
    rdfs.comment = ["Holds Word for main object."]
    range = [Thing]

class hasTag(DataProperty):
    rdfs.comment = ["Holds Tag for main object."]
    range = [str]


class hasPredOntoRel(DataProperty):
    rdfs.comment = ["Holds RDF Predicate for this tripple's main object."]
    range = [str]

class hasSubject(ObjectProperty):
    rdfs.comment = ["Holds Subject for main object."]
    range = [Thing]

class hasObject(ObjectProperty):
    rdfs.comment = ["Holds Object for relation object."]
    range = [Thing]

class hasPredicate(ObjectProperty):
    rdfs.comment = ["Holds Predicate for relation object."]
    range = [Thing]

class hasSPO(ObjectProperty):
    rdfs.comment = ["Holds SPO for relation object."]
    range = [Thing]

class hasRels(ObjectProperty):
    rdfs.comment = ["Holds Rel objectedf captured by this object."]
    range = [Thing]
