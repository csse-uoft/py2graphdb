from ..config import config as CONFIG
import os, tqdm
if os.path.exists(CONFIG.LOG_FILE):  os.remove(CONFIG.LOG_FILE)

import csv, re, datetime, collections, pickle, unicodedata, io, os
import datetime
from copy import copy
import warnings

from owlready2 import default_world, onto_path, DataProperty, rdfs, Thing, ThingClass
from owlready2.prop import DataPropertyClass, PropertyClass, ObjectPropertyClass
from ..ontology.operators import *

onto_path.append('input/ontology_cache/')
exec(f"{CONFIG.PREFIX} = default_world.get_namespace(\"{CONFIG.NM}\")")

rdf_nm =  default_world.get_namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

from ..utils.misc_lib import *
import collections
import uuid
from rdflib import Literal,URIRef
from rdflib.util import from_n3

PREFIX = CONFIG.PREFIX

# class hasUUID(DataProperty):
#     rdfs.comment = ["UUID for the object, if applicable"]
#     range = [str]

# global variable that stores the working dict of data.
# It is used in place of the owlready2 sqllite3, as its more efficient.
global_db = {}
global_db_index_names = CONFIG.DB_INDEX_FIELDS
global_db_indexed = collections.defaultdict(lambda:{})

def logger(text, filename=CONFIG.LOG_FILE):
    """
    logs errors and warnings to the file at filename
    :param text : string value of text to write to log
    :param filename : string value of log's filename
    """
    # Open a file with access mode 'a'
    file_object = open(filename, 'a')
    # Append 'hello' at the end of file
    file_object.write(str(datetime.datetime.today()) + "\t" + str(text) + "\n")
    # Close the file
    file_object.close()

def escape_str(s: str, lower=True):
    """
    Generate an individual/class name that complies the ontology format.
    :param s : string value of string to escape.
    :param lower : whetehr to convert to lower case or not.
    :return s : formatted string
    """
    if lower:
        s = s.lower()
    # string.replace('+', '_plus_')
    s.replace('<', '_lt_')
    s.replace('>', '_gt_')
    s = re.sub(r'[^-_0-9a-zA-Z]', '_', s)
    return re.sub(r'_-_|-_-|_+', '_', s)


def is_bom(file_path):
    """
    check if file contains BOM characters.
    :param file_path: filename of file to check BOM for
    :return True/False whetehr fiel is BOM formatted.
    """
    f = open(file_path, mode='r', encoding='utf-8')
    chars = f.read(4)[0]
    f.close()
    return chars[0] == '\ufeff'


def read_csv(csv_path: str, encoding=None):
    """
    read CSV file, with error handling.
    :param csv_path : string with csv file path
    :param encoding : string with file nencoding to use, if any
    :return data : list of data read from CSV file
    """
    data = []
    if not encoding:
        encoding = 'utf-8-sig' if is_bom(csv_path) else 'utf-8'
    print(f'Loaded CSV "{csv_path}"; Encoding: {encoding}')
    with open(csv_path, encoding=encoding, newline='') as file:
        reader = csv.DictReader(file, quotechar='"', delimiter=',',  quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            data.append(row)
    return data


def write_csv(csv_path, data: list):
    """
    write CSV file
    :param csv_path : string with CSV file name to write to
    :param data : list with records to wrote to CSV file
    """
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def format_strptime(d):
    """
    parse a date string into formatted Timestamp value
    :param d : string with date value to format
    :return : string formatted as Timestamp type
    """
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%d 00:00:00")
    except ValueError:
        try:
            return datetime.datetime.strptime(d, "%Y-%m-%d 00:00")
        except ValueError:
            return datetime.datetime.strptime(d, "%Y-%m-%d")


###########################################################
# Methods for handling instance creation
# Uses internal glbol_db dict for storage
# Created UUID if needed for each instance.
###########################################################
def get_instance_label(klass, uuid_inst=None):
    """
    return instance label with class and UUID
    :param klass: type of instance
    :param uuid_inst: uuid instance, e.g. from uuid.uuid4()
    :return string value of instance label
    """
    if uuid_inst is None:
        uuid_inst = uuid.uuid4()
    klass_label = re.sub(r'^[^\.]+\.','',str(klass).lower())
    inst_id = f"{klass_label}_{uuid_inst}"
    inst_id = resolve_nm_for_dict(inst_id)
    return inst_id


def build_index(batch_count=os.cpu_count()):
    print('Building global_db index...')
    if CONFIG.STORE_LOCAL:
        global global_db_index_names
        global global_db_indexed
    else:
        return
    from concurrent.futures import ThreadPoolExecutor
    props = global_db_index_names.copy()

    search_args = []
    batch_size = len(global_db.keys())//batch_count
    for i,chunk in tqdm.tqdm(enumerate(chunked_dict(global_db.items(), batch_size)), leave=False, desc='loading...', total=batch_count):
        search_args.append([props, i,chunk])

    with ThreadPoolExecutor() as p:
        res_sub = p.map(lambda args, f=build_index_raw: f(*args), search_args)
    res = list(res_sub)
    global_db_indexed = {}
    for prop in props:
        global_db_indexed[prop] = ObjectDict(lambda:PropertyList())

    for d in res:
        for k,v in d.items():
            global_db_indexed[k].update(v)

def build_index_raw(props, i,sub_global_db):
    global_db_index_tmp = {}
    for prop in props:
        global_db_index_tmp[prop] = ObjectDict(lambda:PropertyList())

    for prop in props:
        for inst_id,inst in tqdm.tqdm(sub_global_db, leave=False, desc=f"build {prop} idx({i}"):
            if prop in inst.keys():
                found = None
                if isinstance(inst[prop],(PropertyList, list)):
                    found = inst[prop]
                else:
                    found = [inst[prop]]
                if found:
                    for v in found:
                        global_db_index_tmp[prop][v].append(inst_id)
    
    return global_db_index_tmp



def search_indexed_instances(klass=None, props={}, how='all'):
    if CONFIG.STORE_LOCAL:
        global global_db_indexed
    else:
        return 
    ps = dict([(p,v) for p,v in props.items() if p in global_db_indexed.keys()])
    ps_other = dict([(p,v) for p,v in props.items() if p not in global_db_indexed.keys()])
    inst_ids = set()
    for prop,v in ps.items():
        if len(inst_ids) == 0:
            inst_ids = set(global_db_indexed[prop][v])
        else:
            inst_ids_tmp = set(global_db_indexed[prop][v])
            inst_ids = inst_ids.intersection(inst_ids_tmp)

    sub_global_db = dict([(k,v) for k,v in global_db.items() if k in inst_ids])
    return search_instances(klass=klass, props=ps_other, sub_global_db=sub_global_db, how=how)



def search_instances(klass=None, nm=CONFIG.PREFIX, props={}, how='all', sub_global_db = {}):
    """ 
    return instances based on criteria in klass and props
    if klass is passed, the search is faster
    if single property in props is passed, the search is faster
    """
    if sub_global_db == {}:
        sub_global_db = global_db

    if klass: 
        sub_global_db_tmp = {}
        for inst_id,inst in tqdm.tqdm(sub_global_db.items(), leave=False, desc='klass search'):
            prop = 'is_a'
            v = klass
            if prop in inst.keys():
                if (isinstance(inst[prop],(PropertyList, list)) and v in inst[prop]) or v == inst[prop]:
                    sub_global_db_tmp[inst_id] = inst
    else:
        sub_global_db_tmp = sub_global_db

    res = []
    for inst_id,inst in tqdm.tqdm(sub_global_db_tmp.items(), leave=False, desc='prop search'):
        found = []
        for prop,v in props.items():
            if prop in inst.keys():
                if isinstance(inst[prop],(PropertyList, list)):
                    found.append(v in inst[prop])
                else:
                    found.append(v == inst[prop])
        if len([f for f in found if f]) == len(props.values()):
            res.append(inst_id)
            if how=='first':
                break
    if how=='first':
        if res == []:
            return None
        else:
            return get_instance(inst_id=res[0])
    else:
        return [get_instance(inst_id=r) for r in res]


def update_db_index(inst):
    if CONFIG.STORE_LOCAL:
        global global_db_indexed
        global global_db_index_names
    else:
        return
    if inst is not None and 'ID' in inst.keys():
        inst_id = inst['ID']
        for prop in inst.keys():
            if prop in global_db_index_names:
                if isinstance(inst[prop], (PropertyList, list)):
                    indexed_vals = inst[prop]
                else:
                    indexed_vals = [inst[prop]]
                for indexed_val in indexed_vals:
                    if indexed_val not in global_db_indexed[prop]:
                        global_db_indexed[prop][indexed_val] = []
                    if inst_id not in global_db_indexed[prop][indexed_val]:
                        global_db_indexed[prop][indexed_val].append(inst_id)

class ObjectDict(collections.defaultdict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._snapshot = None

    def snapshot(self):
        self._snapshot = copy(self)

    def ischanged(self):
        return self._snapshot is not None and self._snapshot != self

class PropertyList(list):
    def __iadd__(self,values):
        for value in values:
            self.append(value)
        return self
    
    def __delattr__(prop, val):
        super().__delattr__(val)

    def append(self,value):
        if value not in self:
            super().append(value)


def get_instance(klass=None,nm=CONFIG.PREFIX, inst_id=None, props={}):
    if CONFIG.STORE_LOCAL:
        global global_db
    else:
        global_db = {}
    '''
    return an instance with matching properties, or creates a new instance and returns that
    :param klass: type of the instance
    :param nm: namespace to use, defaults to PREFIX
    :param props: properties used to find or create the instance. 
            Includes namespace in property name (e.g. "time.hasEnd")
            Namespace is removed when runing seaarch, but used when creating a new instance, using exec().
    :return inst
    '''
    inst = None
    uuid_inst = None
    key = None
    key_list = [key for key in props.keys() if 'hasUUID' in str(key)]
    props = dict([k,v] for k,v in props.items() if v is not None)

    if inst_id is not None: inst_id = resolve_nm_for_dict(inst_id)
    if klass is None and inst_id is not None and (CONFIG.STORE_LOCAL and inst_id in global_db.keys()):
        # was created/found before under the inst_id
        # just return without changing anything
        # get any instance and get ID field, in case the first is the properties label
        inst_id = global_db[inst_id]['ID']
        # now get the final one with main inst_id value
        inst = global_db[inst_id]

        return inst

    elif inst_id is not None and (CONFIG.STORE_LOCAL and inst_id in global_db.keys()):
        # was created/found before under the inst_id
        # pased a klass, so process as normal
        inst = global_db[inst_id]
        inst.snapshot()

    elif len(key_list)>0:
        # the UUID was passed, let's use it to build key and find the instance
        key = props[key_list[0]]
        uuid_inst = key
        if inst_id is None:
            inst_id = get_instance_label(klass=klass, uuid_inst=uuid_inst)
        if inst_id in global_db.keys():
            # was created/found before under the inst_id
            inst = global_db[inst_id]
            inst.snapshot()

    
    
    prop_keys = [[str(k),k] for k in props.keys()]
    prop_keys.sort(key=lambda x: x[0])  # changes the list in-place (and returns None)
    properties = dict(collections.OrderedDict({k: props[k] for _,k in prop_keys}))
    if 'is_a' in properties.keys() and properties.get('is_a') is None: del properties['is_a']

    if inst is None and properties != {} and CONFIG.STORE_LOCAL:
        # inst not found and parameters not empty, hence can use parameters as unique search key.
        key = f"{klass}_{properties}"
        if key in global_db.keys():
            inst = global_db[key]
            inst_id = inst['ID']
            inst.snapshot()


    if inst is not None:
        inst.snapshot()
        uuid_prop = eval(nm+'.hasUUID')
        if (inst_id is None and inst['ID']==[]) or (uuid_prop  is not None and inst[uuid_prop] == []):
            uuid_inst = uuid.uuid4()
            inst_id = get_instance_label(klass=klass, uuid_inst=uuid_inst)
            if uuid_prop is not None:       inst[uuid_prop] = str(uuid_inst)
        # update_run_label(inst, nm)
        inst.snapshot()

        for prop,val in properties.items():
            if val is None: continue
            if not isinstance(val, (PropertyList,list)):
                inst[prop] = val
            else:
                inst[prop] = PropertyList(set(val))
    else:
        inst = ObjectDict(lambda:PropertyList(), properties)
        if klass: inst['is_a'] = klass
        if inst_id is None:
            uuid_inst = uuid.uuid4()
            inst_id = get_instance_label(klass=klass, uuid_inst=uuid_inst)
            prop_eval = eval(nm+'.hasUUID')
            if prop_eval is not None:         inst[prop_eval] = str(uuid_inst)

        for prop,val in properties.items():
            if val is None: continue       
            if not isinstance(val, (PropertyList, list)):
                inst[prop] = val
            else:
                inst[prop] = PropertyList(set(val))
        inst.snapshot()
        # update_run_label(inst, force=True)

    if inst['ID'] == []:
        inst['ID'] = inst_id
        # update_run_label(inst, nm)

    inst_id = resolve_nm_for_dict(inst_id)
    inst['ID'] = inst_id

    if key and CONFIG.STORE_LOCAL:  global_db[key] = inst
    if CONFIG.STORE_LOCAL:          global_db[inst_id] = inst
    tmp = inst

    for prop,val in tmp.items():
        if isinstance(val,(PropertyList, list)):
            try:
                inst[prop] = PropertyList(set(val))
            except TypeError  as e:
                print(inst_id, prop, val)
                print(e)
                raise(e)
    if inst_id is None:
        # Something went wrong. Display data and throw exception.
        print("")
        print(inst)
        print(prop)
        print(properties)
        print("")
        raise(Exception("No inst_id"))
    update_db_index(inst)
    return inst

def get_blank_instance(klass, nm=CONFIG.PREFIX, inst_id = None):
    if CONFIG.STORE_LOCAL:
        global global_db
    else:
        global_db = {}
    '''
    return new an instance without any properites, ONLY hasUUID is included
    :param klass: type of the instance
    :param nm: namespace to use, defaults to CONFIG.PREFIX
    :return inst: instance label
    '''
    uuid_inst = uuid.uuid4()
    if inst_id is None:
        inst_id = get_instance_label(klass=klass, uuid_inst=uuid_inst)
    inst = ObjectDict(lambda:PropertyList())
    inst['ID'] = inst_id
    inst['is_a'] = klass
    prop_eval = eval(nm+'.hasUUID')
    if prop_eval is not None:
        inst[prop_eval] = str(uuid_inst)
    # update_run_label(inst, nm)
    inst.snapshot()

    global_db[inst_id] = inst
    update_db_index(inst)
    return inst

# def update_run_label(inst, nm=CONFIG.PREFIX, force=False):
#     if inst is None:
#         return
#     elif CONFIG.RUN_LABEL not in inst[nm+'.hasRunLabel']: 
#         if force or inst.ischanged():
#             inst[nm+'.hasRunLabel'].append(CONFIG.RUN_LABEL)
#             return True
#         else:
#             False
#     else:
#         return False

def encode_inst(val):
    """
    encode OWL instance name to remove any non-OWL characters (punctuation)
    return val : string value of instance label
    """
    puncts = '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~ '
    val = unicodedata.normalize('NFD', val).encode('ascii', 'ignore').decode()
    val = re.sub('|'.join([re.escape(s) for s in puncts]), '_',val)
    val = re.sub(r'_+','_',val)
    return val

def _resolve_nm(val, from_delimiter=':', to_delimiter='.'):
    """
    Resolve the namespace on a property range value. Uses rules and look up table for predefined property range types.
    return res : string value for property value
    """
    if isinstance(val, ThingClass) or issubclass(type(val), PropertyClass):
        val = str(val)

    res = ''
    if isinstance(val, str):
        match = re.findall(f'(.+)\\{to_delimiter}([^\\{to_delimiter}]+)', val)
        if len(match) > 0:
            res = val
        else:
            match = re.findall(f'^\\{to_delimiter}([^\\{to_delimiter}]+)', val)
            if len(match) > 0:
                res = f"{CONFIG.PREFIX}{to_delimiter}{encode_inst(match[0])}"
            else:
                match = re.findall(f'(.*)\\{from_delimiter}([^\\{from_delimiter}]+)', val)
                if len(match) == 0:
                    res = f"{CONFIG.PREFIX}{to_delimiter}{encode_inst(val)}"
                else:
                    if match[0][0] == '': res = f"{CONFIG.PREFIX}{to_delimiter}{encode_inst(match[0][1])}"
                    else: res = f"{match[0][0]}{to_delimiter}{encode_inst(match[0][1])}"
    elif isinstance(val, datetime.datetime):
        res = '"'+val.strftime("%Y-%m-%dT%H:%M:%S")+'"'

    else:
        res = val

    return res
def resolve_nm_for_ttl(val):
    return _resolve_nm(val, from_delimiter='.', to_delimiter=':')
def resolve_nm_for_dict(val):
    return _resolve_nm(val, from_delimiter=':', to_delimiter='.')

def default_to_regular(d):
    """convert collections.defalutdict to dict"""
    if isinstance(d, ObjectDict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    elif isinstance(d, PropertyList):
        d = [default_to_regular(v) for v in d]
    elif isinstance(d,str):
        d.encode(encoding='UTF-8')
    
    return d

def save_global_db(filename='global_db.pickle'):
    """
    save dictionary in global_db to a pickle file.
    value vcan be used later to generate .ttl file without loading all data, or process can be restarted.
    """
    print(f"Saving global_db to pickle file... ({filename})")
    global global_db
    tmp = {}
    for key,val in tqdm.tqdm(global_db.items(), total=len(global_db.keys())):
        tmp[key] = default_to_regular(val)

    with open(filename, 'wb') as handle:
        pickle.dump(tmp, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_global_db(filename='global_db.pickle'):
    """load global_db from pickle file"""
    print(f"Loading global_db from pickle file... ({filename})")
    global global_db

    with open(filename, 'rb') as handle:
        global_db = pickle.load(handle)
    
    for key,val in tqdm.tqdm(global_db.items(), total=len(global_db.keys())):
        global_db[key] = ObjectDict(lambda: PropertyList(),val)


def row_to_turtle(inst, prop_only=False, subclass=False, s_label='s', stype_label='stype'):
    """
    convert dictionary value to Turtle format
    generates variable names for Operator-wrapped properties.
        call row_to_sparql_filters() to get fitlers aligned with tutrle output
    """
    found_properties = False
    if inst.get('ID'):
        s = resolve_nm_for_ttl(inst['ID'])
    else:
        s = f'?{s_label}'

    stype = f"?{stype_label}"
    text = ''
    if not prop_only and inst.get('is_a'):
        if subclass:
            text += f"{s} a [<http://www.w3.org/2000/01/rdf-schema#subClassOf> {resolve_nm_for_ttl(inst['is_a'])}];\n"
        else:
            text += f"{s} a {resolve_nm_for_ttl(inst['is_a'])};\n"
        found_properties = True
    else:
        text += f"{s} "
    for prop_i, (prop,vals) in enumerate(inst.items()):
        op = None
        if isinstance(prop, Operator):
            op = prop
            prop = op.prop

        if prop in ['is_a', 'ID']:
            continue
        if not isinstance(vals,(PropertyList,list)):
            vals = [vals]
        for val in set(vals):
            if val is None:
                continue
            prop2 = str(prop).replace(':','.')
            prop2 = re.sub('^\.', f'{CONFIG.PREFIX}.', prop2)

            if isinstance(prop, (DataPropertyClass,ObjectPropertyClass)):   
                prop_eval = prop
                prop_str = f"<{prop.namespace.base_iri}{prop.name}>"
            elif isinstance(prop2, str):
                prop_eval = eval(prop2)
                prop_str = resolve_nm_for_ttl(prop)
            else:                                       
                prop_eval = prop2
                prop_str = resolve_nm_for_ttl(prop)
            # if str in ranges:       o = '"'+str(val).replace('\\', '\\\\').replace('"','\\"') + '"'
            if prop_eval is None:            o = resolve_nm_for_ttl(val)
            elif str in prop_eval.range:     o = Literal(str(val)).n3()
            elif int in prop_eval.range:     o = Literal(int(val)).n3()
            elif float in prop_eval.range:   o = Literal(float(val)).n3()
            elif bool in prop_eval.range:   o = Literal(bool(val)).n3()
            elif len(prop_eval.range)>0 and prop_eval.range[0] != Thing :     o = Literal(str(val)).n3()+f"^^{prop_eval.range[0]}"
            else:                            o = resolve_nm_for_ttl(val)

            if isinstance(op, Operator):
                text += f"    {prop_str} ?var_{prop_i};\n"
            else:
                text += f"    {prop_str} {o};\n"

            found_properties = True
    text += ".\n"
    if subclass:
        if inst.get('is_a'):
            text += f"FILTER EXISTS {{{stype} <http://www.w3.org/2000/01/rdf-schema#subClassOf> {resolve_nm_for_ttl(inst['is_a'])}}}.\n"
        else:
            warnings.warn("Subclass was requested by no is_a was provided. Ignoring subclass", category=RuntimeWarning)
    return text if found_properties else None

def row_to_sparql_filters(inst, s_label='s'):
    """convert dict with operators to SPARQL FILTER() format"""
    found_properties = False
    if inst.get('ID'):
        s = resolve_nm_for_ttl(inst['ID'])
    else:
        s = f'?{s_label}'
    text = ''

    ivars = []
    for prop_i, (op,vals) in enumerate(inst.items()):
        if not issubclass(type(op), Operator):
            continue
        if not isinstance(vals,(PropertyList,list)):
            vals = [vals]
        filter_vals = []
        for val in set(vals):
            prop = op.prop
            prop2 = str(prop).replace(':','.')
            prop2 = re.sub('^\.', f'{CONFIG.PREFIX}.', prop2)
            op.set_normalized(resolve_nm_for_ttl(prop2))

            if val is None:
                continue
            if isinstance(prop, ObjectPropertyClass):   
                prop_eval = prop
            elif isinstance(prop2, str):
                prop_eval = eval(prop2)
            else:                                       
                prop_eval = prop2

            if prop_eval is None:            o = resolve_nm_for_ttl(val)
            elif str in prop_eval.range:     o = Literal(str(val)).n3()
            elif int in prop_eval.range:     o = Literal(int(val)).n3()
            elif float in prop_eval.range:   o = Literal(float(val)).n3()
            elif bool in prop_eval.range:    o = Literal(bool(val)).n3()
            elif len(prop_eval.range)>0 and prop_eval.range[0] != Thing :     o = Literal(str(val)).n3()+f"^^{prop_eval.range[0]}"
            else:                            o = resolve_nm_for_ttl(val)
            filter_vals.append(o)

        # add the propert/value pair to the query or 
        # if an operator, add ?i_var to query and filter for ?i_var after
        if isinstance(op, (has, hasany, hasall, hasonly, nothas)):
            if not isinstance(vals,(PropertyList,list)):
                filter_vals = [filter_vals]
        elif isinstance(vals,(PropertyList,list)) and len(filter_vals)>0:
            filter_vals = filter_vals[0]
        tmp_var = f'?var_{prop_i}'
        ivars.append({'op':op,'var':tmp_var, 'select':op.to_select(var=tmp_var), 'cond_vals':vals})
        text += f"{op.to_sparql(val=filter_vals, var=tmp_var, owner=s_label)}.\n"

        found_properties = True

    return (text, ivars) if found_properties else (None, None)

def save_db_as_ttl(filename='global_db.ttl', dict_db=None):
    """Save global_db as .ttl file"""
    global global_db
    if dict_db is None:
        dict_db = global_db

    f = io.FileIO(filename, 'w')
    writer = io.BufferedWriter(f,buffer_size=100000000)
    writer.write(TURTLE_PREAMBLE.encode(encoding='UTF-8'))

    flush_i = 0
    flush_cycle = 100000

    records = [inst for inst_id,inst in dict_db.items() if inst_id == inst['ID']]
    for inst in tqdm.tqdm(records, total=len(records)):
        if flush_i % flush_cycle == 0:
            writer.flush()
        flush_i += 1
        klass = eval(inst['is_a'])
        prop_ranges = dict([(prop,prop.range) for prop in list(klass.INDIRECT_get_class_properties())])
        writer.write(row_to_turtle(inst).encode(encoding='UTF-8'))

    writer.flush()



def save_global_db_as_dict(filename='global_db.yaml'):
    """
    save dictionary in global_db to a pickle file.
    value vcan be used later to generate .ttl file without loading all data, or process can be restarted.
    """
    print(f"Saving global_db to yaml file... ({filename})")
    global global_db
    tmp = {}
    records = [(inst_id,inst) for inst_id,inst in global_db.items() if inst_id == inst['ID']]
    import json
    for key,val in tqdm.tqdm(records, total=len(records)):
        tmp[key] = default_to_regular(val)

    with open(filename, "w") as fp:
        json.dump(tmp,fp, indent=4, default=str) 



class SPARQLDict():

    def _clear_graph(graph):
        query = f"CLEAR GRAPH <{graph}>"
        result = CONFIG.client.execute_sparql(query)

    @classmethod        
    def _delete(cls, inst_id, refs=True):
        inst_id = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.', inst_id)
        inst_id = resolve_nm_for_ttl(inst_id)
        query = f"""
            PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
            DELETE {{GRAPH <{CONFIG.GRAPH_NAME}> {{ 
                {inst_id} ?p ?o.
            }}}}
            WHERE {{{inst_id} ?p ?o}}
        """
        if refs:
            query += f""";
                PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
                DELETE {{GRAPH <{CONFIG.GRAPH_NAME}> {{ 
                    ?s ?p {inst_id}.
                }}}}
                WHERE {{?s ?p {inst_id}}};
                """
        result = CONFIG.client.execute_sparql(query)

    @classmethod
    def _add(cls, klass, inst_id=None, props={}):
        inst = get_instance(klass=klass, props=props,inst_id=inst_id)
        ttl_query = row_to_turtle(inst)
        # INSERT
        query = f"""
            PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
            INSERT {{GRAPH <{CONFIG.GRAPH_NAME}> {{{ttl_query}}}}}
            WHERE {{}};
            """

        result = CONFIG.client.execute_sparql(query)
        inst = cls._get(klass=klass, inst_id=inst['ID'])
        return inst

    @classmethod
    def _get(cls, klass=None, inst_id=None, props={}):
        if inst_id is None and props=={}:
            raise(Exception("no criteria"))
        if inst_id is None and props != {}:
            inst = props.copy()
            inst['is_a'] = klass
            ttl_query = row_to_turtle(inst)
            query = f"""
                    PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
                SELECT DISTINCT ?s
                FROM <{CONFIG.GRAPH_NAME}>
                WHERE {{ {ttl_query}   }}
                """
            result = CONFIG.client.execute_sparql(query)
            uris = list(set([r['s']['value'] for r in result["results"]["bindings"] if 's' in r.keys() and r['s']['type']=='uri']))

            if len(uris) > 1:
                raise(Exception(f"too many uris returned:\n{query}\n" + "\n\t".join(uris)))
            elif len(uris) == 1:
                inst_id = uris[0]
                inst_id = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.', inst_id)
            else:
                inst_id = None
                inst = None
 
        if inst_id is not None:
            # if org_inst_id is None:
            inst_id = resolve_nm_for_ttl(inst_id)
            query = f"""
                    PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
                SELECT DISTINCT ?s ?p ?o
                # FROM <{CONFIG.GRAPH_NAME}>
                WHERE {{
                    BIND({inst_id} as ?s).
                    ?s ?p ?o}}
                """
            
            result = CONFIG.client.execute_sparql(query)
            inst_id = resolve_nm_for_dict(inst_id)
            if len(result['results']['bindings']) >0:
                properties = SPARQLDict.sparql_to_dict(result['results']['bindings'])
                properties = {**props, **properties}
                inst = get_instance(klass=klass, inst_id=inst_id, props=properties)
            else:
                inst = None
        
        return inst

    @classmethod
    def _update(cls, klass=None, inst_id=None, drop=None, add=None, new=None, iri=None):
        if inst_id is None:
            return cls._add(klass=klass, props=add or new)
        else:
            found = SPARQLDict._path_exists(start=inst_id, end=None, preds='rdf:type', direction='children', how='first')
            if not found:
                return cls._add(klass=klass, inst_id=inst_id, props=add or new)

        inst_id = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}:', inst_id)
        inst_id = re.sub(f'^{CONFIG.PREFIX}\.', f'{CONFIG.PREFIX}:', inst_id)
        inst = {'ID':inst_id}

        if new is not None:
            query = ''
            for prop in new.keys():
                if isinstance(prop, str) and iri.get(prop):
                    ttl_props = f"<{iri[prop].iri}>"
                elif isinstance(prop, (DataPropertyClass, ObjectPropertyClass)):
                    ttl_props = f"<{prop.iri}>"
                else: # isinstance(prop, str):
                    ttl_props = resolve_nm_for_ttl(prop)

                if ttl_props:
                    query += f"""
                                    PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
                        DELETE WHERE {{GRAPH <{CONFIG.GRAPH_NAME}> {{ 
                            {inst_id} {ttl_props} ?o.
                        }}}};
                    """
            if len(query)>0:
                result = CONFIG.client.execute_sparql(query, method='update')
            add = new
        if drop is not None:
            ttl_props = row_to_turtle({**inst, **drop, }, prop_only=True)
            if ttl_props:
                query = f"""
                            PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
                    DELETE {{GRAPH <{CONFIG.GRAPH_NAME}> {{ 
                        {ttl_props}
                    }}}}
                    WHERE {{}};
                    """
                result = CONFIG.client.execute_sparql(query, method='update')
        if add is not None:
            ttl_props = row_to_turtle({**inst, **add}, prop_only=True)
            if ttl_props:
                query = f"""
                            PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
                    INSERT {{GRAPH <{CONFIG.GRAPH_NAME}> {{ 
                        {ttl_props}
                    }}}}
                    WHERE {{}};
                    """
                result = CONFIG.client.execute_sparql(query, method='update')

        inst = cls._get(klass=klass, inst_id=inst_id)

        return inst

    @classmethod
    def _search(cls, query=None, klass=None, inst_id=None, props={}, order={}, how='first', subclass=False):
        if klass is not None and query is None:
            return cls._search_by_params(klass=klass, inst_id=inst_id, props=props, order=order, how=how, subclass=subclass)
        elif klass is None and query is not None:
            return cls._search_by_query(query=query)
        else:
            raise(ValueError(f"only one of klass and query can be None: klass=\"{klass}\"; query=\"{query}\""))
        
    # @classmethod
    # def _search_by_query(cls, query):
    #     separator = "###"
    #     query = """
    #             PREFIX utest: <http://utest/#>
    #             SELECT DISTINCT *
    #             WHERE { 
    #             #    BIND(utest:n1 as ?start).
    #                 ?s utest:title ?val;
    #                     utest:desc ?list.
    #             #    OPTIONAL{?start utest:hasListOfURIs ?l1}
    #             #    filter(?val > 2).

    #             } limit 1
    #         """
    #     result = CONFIG.client.execute_sparql(query)
    #     # from src.py2graphdb.utils.db_utils import *

    #     for res in result['results']['bindings']:
    #         properties = SPARQLDict.sparql_to_dict(props=res, separator=separator)
    #         # todo: update resolve_nm_for_dict to resolve this correctly
    #         klass_tmp = properties.get('is_a') or klass
    #         klass_tmp = re.sub('^\.', f'{CONFIG.PREFIX}.', str(klass_tmp))
    #         inst = get_instance(klass=klass_tmp, inst_id=properties.get('ID'), props=properties)
    #         results.append(inst)                

    #     return results

    @classmethod
    def _search_by_params(cls, klass=None, inst_id=None, props={}, order={}, how='first', subclass=False):
        results = []
        separator = '###'
        inst_wrapper = props.copy()
        inst_wrapper['ID'] = inst_id
        inst_wrapper['is_a'] = klass
        ttl_query = row_to_turtle(inst_wrapper, subclass=subclass) or ''
        filter_query, filter_ivars = row_to_sparql_filters(inst_wrapper) or ''

        grounded_props = [p for p in inst_wrapper.keys() if issubclass(type(p), PropertyClass)]
        filter_props = [p.prop for p in inst_wrapper.keys() if issubclass(type(p), Operator)]
        klass_object = eval(f"{resolve_nm_for_dict(klass)}")
        try:
            klass_object.relations
            if subclass:
                relations = list(set(flatten([[k2['pred']for k2 in k.relations.values()]  for k in eval(f"{resolve_nm_for_dict(klass)}.subclasses()")])))
            else:
                relations = [v['pred'] for v in eval(f"{resolve_nm_for_dict(klass)}.relations.values()")]
        except AttributeError:
            relations = []
        prop_vars = dict([[f"o{pi}", p] for pi,p in enumerate(relations)])
        optional_prop_vars = dict([(pv,p) for pv,p in prop_vars.items() if p not in grounded_props + filter_props])
        query_rels = f"BIND({resolve_nm_for_ttl(inst_wrapper.get('ID'))} as ?s).\n" if inst_wrapper.get('ID') else ''
        query_rels += "?s a ?stype.\n"
        
        for pv,p in optional_prop_vars.items():
            if p not in grounded_props + filter_props:
                query_rels += f"OPTIONAL{{?s {resolve_nm_for_ttl(p)} ?{pv}_0 }}\n" 

        query_select = ' '.join([f"(GROUP_CONCAT(?{pv}_0; separator='{separator}') AS ?{pv})" for pv in prop_vars.keys()])

        if filter_query and filter_ivars:
            query_select += ' ' + ' '.join([ivar_dict['select'] for ivar_dict in filter_ivars])
            limit_str = ''
        else:
            limit_str = 'LIMIT 1' if how=='first' else ''

        #     query_select += ' ' + ' '.join([f"(concat('{separator}',GROUP_CONCAT({ivar_dict['var']}; separator='{separator}'),'{separator}') AS {ivar_dict['var']}_has)" for ivar_dict in filter_ivars])
        # need to exclude graph for subclasses, if outside of this graph
        graph_query = ''#f"FROM <{CONFIG.GRAPH_NAME}>" if not subclass else ''

        where_query = ''
        if ttl_query is not None: where_query += ttl_query
        where_query += query_rels
        if filter_query is not None: 
            if (len(where_query.strip())>0) and (not where_query.strip().endswith('.')):
                where_query +=  '.'
            where_query += '\n'+filter_query
        if order == {}:
            order_str = ""
        else:
            # relations = [f"resolve_nm_for_dict(p) 
            rels = []
            for p,direction in order.items():
                if direction in ['desc', 'descending']:
                    rels.append(f"DESC({resolve_nm_for_ttl(p)})")
                else:
                    rels.append(resolve_nm_for_ttl(p))
            order_str = f"ORDER BY {' ' .join(rels)}"

        prefixes = {}
        for p in prop_vars.values():
            prefixes[p.namespace.name] = p.namespace.base_iri
        prefixes_str = "\n".join([f"PREFIX {pv}: <{p}>" for pv,p in prefixes.items()])

        query = f"""
            PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            {prefixes_str}
            SELECT DISTINCT ?s ?stype {query_select}
            {graph_query}
            WHERE {{ 
                {where_query}
                filter(?stype != owl:Thing).    # to ensure Thing is not included when infer=True
                }}
            # {order_str}
            GROUP BY ?s ?stype
            {limit_str}
            """

        result = CONFIG.client.execute_sparql(query, method='select', infer=False)
        for res in result['results']['bindings']:
            passed_filter = True
            if filter_ivars:
                for filter_ivar in filter_ivars:
                    if isinstance(filter_ivar['op'], (hasonly,hasall)) and filter_ivar['op'].to_select_var is not None:
                        cond_var = re.sub(r'^\?', '', filter_ivar['op'].to_select_var)
                        range = filter_ivar['op'].prop.range
                        kind = range[0] if len(range)>0 else str
                        cond_vals = set(filter_ivar['cond_vals'])
                        found_vals = []
                        for val in res[cond_var]['value'].split(separator):
                            if kind==bool:    
                                val = 'true' == re.sub(f'^{CONFIG.PREFIX}:','',str(val)).lower()
                            elif kind != Thing:
                                val = kind(val) #eval(f"{kind.__name__}(re.sub(f'^{CONFIG.PREFIX}:','',str(val)))")
                            else:
                                val = val.replace(CONFIG.NM,CONFIG.PREFIX+'.')
                            found_vals.append(val)
                        found_vals = set(found_vals)
                        if (isinstance(filter_ivar['op'], hasall) and cond_vals.intersection(found_vals) != cond_vals):
                            passed_filter = False
                            break
                        elif  (isinstance(filter_ivar['op'], hasonly)):
                            tmp_id = res['s']['value'].replace(CONFIG.NM,CONFIG.PREFIX+'.')
                            matched_vals = cond_vals.intersection(found_vals)
                            sub_res = SPARQLDict._process_path_request(tmp_id, None, action='neighbours', preds=[filter_ivar['op'].prop], direction='children', how='all')
                            sub_res = set([v['end'] for v in sub_res])
                            if len(cond_vals) != len(matched_vals) or len(sub_res) != len(matched_vals):
                                passed_filter = False
                                break
                    
            
            if passed_filter:
                properties = SPARQLDict.sparql_to_dict(props=res, prop_vars=prop_vars, separator=separator)
                klass_tmp = properties.get('is_a') or klass
                klass_tmp = resolve_nm_for_dict(klass_tmp)
                inst = get_instance(klass=klass_tmp, inst_id=properties.get('ID'), props=properties)
                results.append(inst)                
                if how=='first':
                    break

        return results

    

    # find parents with pred
    # ask if any parents with pred
    # find children with pred
    @classmethod
    def _path_distance(cls, start, end=None, preds=[], direction='children', how='first', infer=False):
        return cls._process_path_request(start=start, action='distance', end=end, preds=preds, direction=direction, how=how, infer=infer)

    @classmethod
    def _path_exists(cls, start, end=None, preds=[], direction='children', how='first', infer=False):
        return cls._process_path_request(start=start, action='ask', end=end, preds=preds, direction=direction, how=how, infer=infer)

    @classmethod
    def _children(cls, start, end=None, preds=[], action='collect', how='first', infer=False):
        return cls._process_path_request(start=start, action=action, end=end, preds=preds, direction='children', how=how, infer=infer)
    @classmethod
    def _parents(cls, start, end=None, preds=[], action='collect', how='first', infer=False):
        return cls._process_path_request(start=start, action=action, end=end, preds=preds, direction='parents', how=how, infer=infer)
    @classmethod
    def _path_collect(cls, start, end=None, preds=[], action='collect', direction='children', how='first', infer=False):
        return cls._process_path_request(start=start, action=action, end=end, preds=preds, direction=direction, how=how, infer=infer)


    @classmethod
    def _build_node_query(cls, param, val):
        _query = ''
        if isinstance(param, str) or issubclass(type(param), Thing):
            _query = f"BIND({resolve_nm_for_ttl(str(param))} as ?{val})."
        elif isinstance(param, dict):
            _query = ttl_query = row_to_turtle(param, subclass=True, s_label=val)
        elif isinstance(param, (list, PropertyList)):
            inst_ids = []
            props = []
            for p in param:
                if isinstance(p, str):                      inst_ids.append(p)
                elif issubclass(type(p), PropertyClass):    props.append(p)
                elif issubclass(type(p), Operator):
                    # TODO: set Operator with filter
                    props.append(p.prop)

            if len(inst_ids) == 1:
                _query = f"BIND({resolve_nm_for_ttl(str(param))} as ?{val})."
            elif len(inst_ids) > 1:
                _query += f"values ?{val} {{"+ ' '.join([resolve_nm_for_ttl(node) for node in inst_ids]) +"}."

            if len(props) > 0:
                _query += f"?{val} "+ ';'.join([f"{resolve_nm_for_ttl(p)} ?ignore_{pi} " for pi,p in enumerate(props)]) +"."
        return _query

    @classmethod
    # start: string = one inst_id
    #        list (strings)  = many inst_ids
    #        list (Data/ObjectProperty)  = many predicates
    #        dict   = inst object
    def _process_path_request(cls, start, end, action='collect', preds=[], direction='children', how='first', infer=False):
        start_query = SPARQLDict._build_node_query(param=start, val='start')
        if start_query == '':
            raise(ValueError("start condition can't be empty."))

        end_query = SPARQLDict._build_node_query(param=end, val='end')
        if end_query == '':
            warnings.warn("end condition is empty and will search the entire graph.", category=RuntimeWarning)

        limit_bind_query = ''
        limit_query = ''
        if action in ['collect', 'neighbours']:
            action_query = 'SELECT DISTINCT ?path ?start ?middle2 ?end ?index' 
            if how=='first':
                limit_bind_query = 'filter(?path = 0).'
        elif action == 'ask':
            action_query = 'ASK' 
        elif action=='distance':
            action_query = 'SELECT DISTINCT ?distance ?start ?end' 
            if how=='first':
                limit_query = 'LIMIT 1'

        if action != 'distance' and how == 'first':              search_type_query = 'path:allPaths'
        elif action != 'distance' and how == 'shortest':         search_type_query = 'path:shortestPath'
        elif action != 'distance' and how == 'all':              search_type_query = 'path:allPaths'
        elif action == 'distance':                               search_type_query = 'path:distance'


        if 'allPaths' in search_type_query:
            binding_query = """
                path:pathIndex ?path ;
                path:startNode ?middle1;
                path:endNode ?middle2;
                path:resultBindingIndex ?index;
            """
        elif 'shortestPath' in search_type_query:
            binding_query = """
                path:pathIndex ?path ;
                path:startNode ?middle1;
                path:endNode ?middle2;
                path:resultBindingIndex ?index;
            """
        elif 'distance' in search_type_query:
            binding_query = """
                path:distanceBinding ?distance;
                path:startNode ?middle1;
                path:endNode ?middle2;
            """

        if direction == 'parents'    :       direction_query = '^'
        elif direction == 'children' :       direction_query = ''

        pred_query = ''
        if preds and len(preds)>0:
            if isinstance(preds,str):
                pred_list = preds
            elif isinstance(preds, (list, PropertyList)):
                pred_list = "("+'|'.join([f"{direction_query}{resolve_nm_for_ttl(pred)}" for pred in preds])+")"
            else:
                pred_list = None
            if pred_list:
                pred_query = f"""
                    SERVICE <urn:path> {{
                            ?middle1 {pred_list} ?middle2.
                        }}
                    """

        graph_query = ''# f"FROM NAMED <{CONFIG.GRAPH_NAME}>"

        query = f"""
            PREFIX path: <http://www.ontotext.com/path#>
            PREFIX {CONFIG.PREFIX}: <{CONFIG.NM}>
            {action_query}
            {graph_query}
            WHERE {{ 
                {start_query}
                {end_query}
                SERVICE <http://www.ontotext.com/path#search> {{
                    <urn:path> path:findPath {search_type_query} ;
                            path:sourceNode ?start ;
                            path:destinationNode ?end ;
                            {binding_query}.
                    {pred_query}
                }}
                {limit_bind_query}
        }}    ORDER BY ?path ?index {limit_query}
        """

        result = CONFIG.client.execute_sparql(query, method='select', infer=infer)
        if action =='ask'       : return result.get('boolean')
        if action == 'distance' : return cls._parse_distance_list(result['results']['bindings'])
        if action in 'collect'  : 
            tmp = cls._parse_path_list(result['results']['bindings'])
            if how=='first'     : return tmp[0] if len(tmp)>0 else None
            else                : return tmp
        if action in 'neighbours'  : 
            tmp = cls._parse_path_list(result['results']['bindings'])
            tmp = [t for t in tmp if len(t['path'])==0]
            if how=='first'     : return tmp[0] if len(tmp)>0 else None
            else                : return tmp


    @classmethod
    def _parse_distance_list(cls, result):
        path = []
        for node in result:
            path.append({
                'd'  : int(node['distance']['value']),
                's'  : node['start']['value']  if node.get('start') else None,
                'e'  : node['end']['value']  if node.get('end') else None,
            })

        path_list = []
        for ps in sorted(path, key=lambda d: d['d']):
            path_list.append({
                'start'     : resolve_nm_for_dict(re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.'       , ps['s'])),
                'end'       : resolve_nm_for_dict(re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.'       , ps['e'])),
                'distance'  : ps['d'],
            })
        return path_list

    @classmethod
    def _parse_path_list(cls, results):
        path = []
        for node in results:
            path.append({
                's'  : node['start']['value'] if node.get('start') else None,
                'e'  : node['end']['value'] if node.get('end') else None,
                'm'  : node['middle2']['value'],
                'p'  : int(node['path']['value']),
                'i'  : int(node['index']['value']),
            })

        res = ObjectDict(list)
        for d in path[::-1]:
            res[(d['p'], d['e'])].append({
                's' : d['s'],
                'm' : d['m'],
                'e' : d['e'],
                'i' : d['i'],
            })
        path_list = []
        for ps in res.values():
            ps = sorted(ps, key=lambda d: d['i']) 
            tmp = {
                'start' : resolve_nm_for_dict(re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.'   , ps[0]['s']))  if ps[0].get('s') else None,
                'end'   : resolve_nm_for_dict(re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.'   , ps[0]['e'])) if ps[0].get('e') else None,
                'path'  : [resolve_nm_for_dict(re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.'  , d['m'])) for d in ps if d['m'] not in [d['s'],d['e']] ],
            }
            if tmp['end'] is None:
                tmp['end'] = tmp['path'].pop()
            path_list.append(tmp)
        return path_list

    @classmethod
    def sparql_to_dict(cls, props, prop_vars=None, separator=None):
        if prop_vars is None:
            return cls.sparql_to_dict_from_spo(props=props)
        else:
            return cls.sparql_to_dict_from_prop_vars(props=props, prop_vars=prop_vars, separator=separator)

    @classmethod
    def sparql_to_dict_from_spo(cls, props):
        klass = None
        inst_id = None
        properties = ObjectDict(lambda:PropertyList())
        for prop in props:
            s = prop['s']['value']
            s = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.', s)
            p = prop['p']['value']
            p = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.', p)
            val = prop['o']['value']
            val = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.', val)
            inst_id = s
            if p ==  f"{rdf_nm.base_iri}type":
                klass = eval(_resolve_nm(default_world.get_namespace(val).name, from_delimiter='#',to_delimiter='.'))
                if klass is not None: properties['is_a'] = klass
            else:
                if p.startswith('http'):
                    prop_eval = _resolve_nm(default_world.get_namespace(p).name, from_delimiter='#',to_delimiter='.')
                else:
                    prop_eval = p.replace(':','.')
                prop_eval = re.sub('^\.', f'{CONFIG.PREFIX}.', prop_eval)
                prop_eval = eval(prop_eval)
                # if prop_eval in prop_ranges.keys() and len(prop_ranges[prop_eval])>0:
                #     ranges = prop_ranges[prop_eval]
                if prop_eval is None:            o = resolve_nm_for_ttl(val)
                elif str in prop_eval.range:     o = str(val)
                elif int in prop_eval.range:     o = int(val)
                elif float in prop_eval.range:   o = float(val)
                elif bool in prop_eval.range:    o = val == 'true'
                elif len(prop_eval.range)>0:     o = str(val)
                else:                            o = resolve_nm_for_ttl(val)

                try:
                    if 'hasUUID' in str(prop_eval):
                        if prop_eval is not None:   properties[prop_eval] = o
                    else:
                        properties[prop_eval].append(o)
                except:
                    pass
        if inst_id is not None: properties['ID'] = inst_id
        return properties

    @classmethod
    def sparql_to_dict_from_prop_vars(cls, props, prop_vars=None, separator=None):
        properties = ObjectDict(lambda:PropertyList())
        s = props['s']['value']
        s = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.', s)

        inst_id = s

        if props.get('stype'):
            klass = props['stype']['value']
            properties['is_a'] = eval(_resolve_nm(default_world.get_namespace(klass).name, from_delimiter='#',to_delimiter='.'))
        for prop_var,prop in prop_vars.items():
            klass = None
            if prop_var not in props.keys():
                continue

            vals = props[prop_var]['value']
            if separator:   vals = vals.split(separator)
            else:           vals = [vals]
            for val in vals:
                val = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.', str(val))
                val = re.sub(f'^{CONFIG.NM}', f'{CONFIG.PREFIX}.', val)
                if val == '':
                    continue
                try:
                    prop_eval = eval(prop.replace(':','.')) if isinstance(prop,str) else prop
                    # if prop_eval in prop_ranges.keys() and len(prop_ranges[prop_eval])>0:
                    #     ranges = prop_ranges[prop_eval]
                    if prop_eval is None:            o = resolve_nm_for_ttl(val)
                    elif str in prop_eval.range:     o = str(val)
                    elif int in prop_eval.range:     o = int(val)
                    elif float in prop_eval.range:   o = float(val)
                    elif bool in prop_eval.range:    o = val == 'true'
                    elif Thing in prop_eval.range:   o = val
                    elif len(prop_eval.range)>0:     o = str(val)
                    else:                            o = resolve_nm_for_ttl(val)

                    if 'hasUUID' in str(prop_eval):
                        if prop_eval is not None:         properties[prop_eval] = o
                    else:
                        properties[prop_eval].append(o)
                except ValueError:
                    pass
        if inst_id is not None: properties['ID'] = inst_id
        return properties

