from rdflib import Namespace, Graph
from rdflib.namespace import RDFS
from rdflib.namespace import XSD
import rdflib

# one shared URI and prefix for all classes and relations of BiodivMetaO
bmo = Namespace("https://w3id.org/bmo/")
schema = Namespace("https://schema.org/")
owl = Namespace("https://owl.org/")
wd = Namespace("http://www.wikidata.org/entity/")
dbr = Namespace("https://dbpedia.org/resource/")
dct = Namespace("http://purl.org/dc/terms/")

onto = rdflib.URIRef(bmo.BMO)

# init empty graph
g = Graph(identifier=bmo, base=bmo)

# retrieve namespace manager from the graph
nm = g.namespace_manager

# bind it to the namespace manager
nm.bind('bmo', bmo)
nm.bind('schema', schema)
nm.bind('wd', wd)
nm.bind('dct', dct)
nm.bind('dct', dct)
