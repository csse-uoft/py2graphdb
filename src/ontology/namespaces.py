from owlready2 import default_world, onto_path
onto_path.append('ontology_cache/')

# If use graphDB
# If authentication required, set username='grapdb login username', password='graphdb login password'
# default_world.set_backend(backend="sparql-endpoint",
#                           endpoint="http://localhost:7200/repositories/compass-test", debug=False)
try:
    default_world.set_backend(filename='./3.sqlite')
except:
    print("loaded???")#sqlite3.OperationalError
print('Loading/Downloading ontologies, if the script stuck here, try re-run it.')
# compass = default_world.get_ontology('https://github.com/csse-uoft/compass-ontology/releases/download/latest/compass.owl').load(reload=True)
compass = default_world.get_ontology('https://github.com/csse-uoft/compass-ontology/releases/download/latest/compass.owl').load(reload=True)
print('Ontology Loaded.')
cp = default_world.get_namespace('http://helpseeker.co/compass#')  # Same as compass
ic = default_world.get_namespace('http://ontology.eil.utoronto.ca/tove/icontact#')
geo = default_world.get_namespace('http://www.w3.org/2003/01/geo/wgs84_pos/')
cids = default_world.get_namespace('http://ontology.eil.utoronto.ca/cids/cids#')
sch = default_world.get_namespace('https://schema.org/')
org = default_world.get_namespace("http://ontology.eil.utoronto.ca/tove/organization#")
time = default_world.get_namespace("http://www.w3.org/2006/time#")
schema = default_world.get_namespace("https://schema.org/")
dcterms = default_world.get_namespace("http://purl.org/dc/terms/")
activity = default_world.get_namespace('http://ontology.eil.utoronto.ca/tove/activity#')
landuse_50872 = default_world.get_namespace('http://ontology.eil.utoronto.ca/5087/2/LandUse/')
