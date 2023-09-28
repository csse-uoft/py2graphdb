# py2graphdb
Python wrapper for GraphDB and SPARQL interface

Required [OntoText](https://www.ontotext.com/products/graphdb/download) installed locally, running on [http://localhost:7200](http://localhost:7200). This can be changed in the [config/local_config.yml](config/local_config.yml) file)
## Setup
`conda env create -f Py2GraphDB.yml`

## To run example
`conda activate Py2GraphDB`

`python -m src.py2graphdb.main`

## To run unit tests
`conda activate Py2GraphDB`

`python -m unittest`
