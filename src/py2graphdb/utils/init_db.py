import os
def init_db():
    from py2graphdb.config import config as CONFIG
    from owlready2 import default_world
    nm = default_world.get_ontology(CONFIG.NM)

    with nm:
        from py2graphdb.utils.db_utils import SPARQLDict
        from .Model.controller.ks import Ks

    from graphdb_importer import import_and_wait, set_config
    TMP_DIR = './tmp/'
    _ = os.makedirs(TMP_DIR) if not os.path.exists(TMP_DIR) else None
    owl_file = f'{TMP_DIR}init-ontology.owl'
    nm.save(owl_file)
    set_config(CONFIG.SERVER_URL, CONFIG.REPOSITORY, username='admin', password='admin')
    import_and_wait(owl_file, replace_graph=True)
    SPARQLDict._clear_graph(graph=CONFIG.GRAPH_NAME)
    Ks.initialize_ks_db()


def load_owl(owl_file, graph_name=None):
    from py2graphdb.config import config as CONFIG
    if graph_name is None: graph_name = CONFIG.GRAPH_NAME
    from graphdb_importer import import_and_wait, set_config
    set_config(CONFIG.SERVER_URL, CONFIG.REPOSITORY, username='admin', password='admin')
    import_and_wait(owl_file, named_graph=graph_name, replace_graph=False)


