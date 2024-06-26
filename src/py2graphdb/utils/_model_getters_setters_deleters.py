from __future__ import annotations
import re
@classmethod
def search(cls, props={}, how='first', subclass=False):
    insts = SPARQLDict._search(klass=cls.klass, props=props, how=how, subclass=subclass)
    return [cls(inst=inst).cast_to_graph_type() for inst in insts]

@classmethod
def get(cls, inst_id):
    inst = None
    how='first'
    subclass=False
    insts = SPARQLDict._search_by_params(inst_id=inst_id, how=how, subclass=subclass)
    if len(insts)>0:
        inst = cls(inst=insts[0]).cast_to_graph_type()
    return inst


def save(self):
    updates = {}
    iri_updates = {}

    for val, props in self.relations.items():    
        pred = re.sub('^\.', f'{CONFIG.PREFIX}.', str(props['pred']))
        value = getattr(self, f'_{val}')
        # combine updates and IRIs
        updates[pred] = value
        iri_updates[pred] = props['pred']

    # perform a single update operation
    if updates:
        inst = SPARQLDict._update(klass=self.klass, inst_id=self.inst_id, new=updates, iri=iri_updates)
        self.graph_is_a = inst.get('is_a') if inst else None




def delete(self, refs=True):
    SPARQLDict._delete(inst_id=self.inst_id, refs=refs)

def load(self, inst=None):
    if inst is not None and inst.get('ID'):
        self.inst_id = inst['ID']

    if inst is None and self.inst_id is not None:
        inst = self.SPARQLDict._get(inst_id=self.inst_id)
        if inst is None  and self.keep_db_in_synch:
            inst = self.SPARQLDict._add(klass=self.klass,inst_id=self.inst_id)

    elif inst is None and self.inst_id is None and self.keep_db_in_synch:
        inst = self.SPARQLDict._add(klass=self.klass)

    if inst is not None:
        if self.inst_id is not None and self.inst_id != inst['ID']:
            raise(ValueError, f"Unmatched inst_ids: {self.inst_id} != {inst['ID']}")

        if self.inst_id is None:
            self.inst_id = inst['ID']

    if inst is not None:    
        for val,props in self.relations.items():
            pred = props['pred']
            cardinality = props['cardinality']
            if props.get('range'):
                pred.range = props.get('range')
            kind = pred.range[0] if len(pred.range)>0 else str
            values = inst[pred] if pred in inst.keys() else []

            if kind==bool:    
                values = ['true' == re.sub(f'^{CONFIG.PREFIX}:','',str(value)).lower() for value in values]
            elif kind != self.Thing:
                values = [eval(f"{kind.__name__}(re.sub(f'^{CONFIG.PREFIX}:','',str(value)))") for value in values]
            try:
                if cardinality!='many':
                    exec(f"self._{val} = None")
                    values = None if len(values)==0 else values[0]
                else:
                    exec(f"self._{val} = []")
            except AttributeError:
                pass
            exec(f"self._{val} = values")
    else:
        for val,props in self.relations.items():
            pred = props['pred']
            cardinality = props['cardinality']
            try:
                if cardinality != 'many':
                    exec(f"self._{val} = None")
                else:
                    exec(f"self._{val} = []")
            except AttributeError:
                pass

    if inst is not None: 
        self.graph_is_a = inst.get('is_a')
        if isinstance(self.graph_is_a, str):
            tmp = _resolve_nm(default_world.get_namespace(self.graph_is_a).name, from_delimiter='#',to_delimiter='.')
            self.graph_is_a = eval(tmp)


for val,props in relations.items():
    pred = props['pred']
    pred_str = re.sub('^\.', f'{CONFIG.PREFIX}.', str(props['pred']))
    pred_iri = props['pred'].iri
    props_str = str(props['pred'])
    cardinality = props['cardinality']
    if props.get('range'):
        pred.range = props.get('range')
    kind = pred.range[0] if len(pred.range)>0 else str
    kind_str = Thing if isinstance(kind,str) else kind.__name__
    value = 'value'

    if kind==bool:    value = f"{kind_str}('true' == re.sub(f'^{CONFIG.PREFIX}:','',str(value)).lower())"
    elif kind!=Thing:    value = f"{kind_str}(re.sub(f'^{CONFIG.PREFIX}:','',str(value)))"
    else:               value = 'resolve_nm_for_dict(value)'
    set_code = ".append(value)" if cardinality=='many' else " = value"

    code = f"""
@property
def {val}(self):
    return self._{val}

@{val}.setter
def {val}(self,value):
    klass = "{klass}"
    value = {value}
    inst = None
    if isinstance(self._{val}, (PropertyList,list)):
        self._{val}.append(value)
        if self.keep_db_in_synch:
            inst = SPARQLDict._update(klass=klass,inst_id=self.inst_id, add={{{pred_str}:value}}, iri="{{{pred_str}:{props_str}}}")
    else:
        self._{val} = value
        if self.keep_db_in_synch:
            inst = SPARQLDict._update(klass=klass,inst_id=self.inst_id, new={{{pred_str}:value}}, iri="{{{pred_str}:{props_str}}}")
    if self.inst_id is None and inst:
        self.inst_id = inst['ID']    
"""
    exec(code)
    # remove temporary variables
    del code
    del val
    del pred
    del props
    del cardinality
    del kind
    del kind_str
    del value
    del set_code
