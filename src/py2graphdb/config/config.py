from ..utils.sparql_client import SparqlClient
import yaml, os, ast
from yaml.loader import SafeLoader

CONFIG_PATH = open('./src/py2graphdb/config/import_config_path.txt').readlines()[0].strip()

if CONFIG_PATH.startswith('~/'):
    CONFIG_PATH = os.path.expanduser("~") + CONFIG_PATH.replace('~/','/')

# Open the file and load the file
with open(CONFIG_PATH) as f:
    data = yaml.load(f, Loader=SafeLoader)
    for var,val in data.items():
        if isinstance(val,str):
            if val is None or val == 'None':
                exec(f"{var} = {val}")
            else:
                if val.startswith('~/'):
                    val = os.path.expanduser("~") + val.replace('~/','/')
                exec(f"{var} = \"{val}\"")
        else: exec(f"{var} = {val}")

# admin_dict = ast.literal_eval(os.environ['PIPELINE_ADMIN'])
admin_dict = {'username':'admin', 'psw':'admin'}
client = SparqlClient(f"{SERVER_URL}/repositories/{REPOSITORY}", username=admin_dict['username'],password=admin_dict['psw'])
