from os.path import join
from os import listdir
import pandas as pd
from rdflib import Literal
from rdflib.namespace import RDF, SKOS

from utils.mappings import *
from utils.namespaces import *
from utils.data_structure import MyNode, MyLiteral
from random import seed, randint
from validate_values import validate
import meta_config
from config import solved_path, results_root_path

seed(1)


def add_kg_metadata(g):
    g.add((onto, RDF.type, SKOS.ConceptScheme))
    g.add((onto, dct.title, Literal(meta_config.schema_title, lang="en")))
    g.add((onto, dct.description, Literal(meta_config.schema_description, lang="en")))
    g.add((onto, dct.license, Literal(meta_config.license_url)))
    g.add((onto, dct.created, Literal(meta_config.created_at, datatype=XSD.date)))
    creator = rdflib.BNode()
    g.add((creator, schema.name, Literal(meta_config.author)))
    g.add((creator, schema.identifier, Literal(meta_config.orcid)))
    affiliation = rdflib.BNode()
    g.add((affiliation, schema.name, Literal(meta_config.institute)))
    g.add((affiliation, schema.url, Literal(meta_config.institute_url)))
    g.add((creator, schema.affiliation, affiliation))
    g.add((onto, dct.creator, creator))


def load_solved_dataset():
    # loads the solved datasets one by one
    files = listdir(solved_path)
    for f in files[0:]:
        df = pd.read_csv(join(solved_path, f), header=0)
        mapping = []
        for p, v, original_key in zip(df['Prediction'].tolist(), df['Metadata Value'].tolist(),
                                      df['Metadata Key'].tolist()):
            if p != 'Not Mapped':
                if validate.is_valid(v, p):
                    mapping.append((p, v, original_key))
                # else:
                #     print('Invalid entry {} {}'.format(p, v))

        yield mapping


def get_literal_name(obj):
    # this method overrides the prediction if the original clean key of the literal is in supported literals
    litName = obj[2].split('.')
    litName = litName[len(litName) - 1]
    litName = litName.split('_')[0]
    if litName not in supported_literals.keys():
        concepts = obj[0].split('_')
        litName = concepts[len(concepts) - 1]
    return litName


def add_node(node, s, g):
    # recursively adding nodes with their members and literals
    node.name = node.name.split('_')[0]

    p = rdflib.URIRef('{}{}'.format(bmo, node.name))
    o = rdflib.BNode()

    if node.is_a:
        g.add((o, RDF.type, node.is_a))
    if node.exactMatch:
        g.add((o, SKOS.exactMatch, node.exactMatch))
    if node.closeMatch:
        g.add((o, SKOS.closeMatch, node.closeMatch))

    g.add((s, p, o))
    if node.literals:
        for l in node.literals:
            p_l, lbl = get_relation(l.name)
            g.add((p_l, RDFS.label, Literal(lbl)))
            g.add((o, p_l, Literal(l.value, datatype=l.datatype)))
    if node.members:
        for child in node.members:
            return add_node(child, o, g)


def parse_concepts(obj, created):
    instance = None
    tmp = obj[2].split('_')
    if len(tmp) == 2:
        instance = tmp[1]

    key = obj[0]
    concepts = key.split('_')
    len_concepts = len(concepts)
    for i in range(len_concepts):
        nodeName = concepts[i]
        if instance:
            nodeName += '_{}'.format(instance)

        if i == 0:
            if nodeName not in created.keys():
                # this overrides the node name to hold instance info
                is_a, exactMatch, closeMatch = get_node_type(nodeName)
                myNode = MyNode(name=nodeName, is_a=is_a, exactMatch=exactMatch, closeMatch=closeMatch,
                                members=[], literals=[])
                created[nodeName] = {'node': myNode}
        elif i + 1 == len_concepts:
            # retrieve parentNode
            parentName = concepts[i - 1]
            targetConcept = concepts[0]
            if instance:
                parentName += '_{}'.format(instance)
                targetConcept += '_{}'.format(instance)

            parentNode = [m for m in created[targetConcept]['node'].members if m.name == parentName]
            if parentNode:
                parentNode = parentNode[0]
            else:

                parentName = concepts[0]
                if instance:
                    parentName += '_{}'.format(instance)

                parentNode = created[parentName]['node']

            val = obj[1]
            litName = get_literal_name(obj)
            lit = MyLiteral(name=litName, value=val, datatype=get_literal_type(litName))
            parentNode.literals += [lit]
        else:
            # retrieve parentNode
            parentName = concepts[i - 1]
            if instance:
                parentName += '_{}'.format(instance)

            # retrieve parentNode
            parentNode = created[parentName]['node']
            # if there are member and those member has no occurance of the current node
            addedMember = [m for m in parentNode.members if m.name == nodeName]
            if not addedMember:
                is_a, exactMatch, closeMatch = get_node_type(nodeName)
                parentNode.members += [MyNode(name=nodeName, is_a=is_a, exactMatch=exactMatch, closeMatch=closeMatch,
                                              members=[], literals=[])]


def find_object_add_them(objects, s, g):
    # my created root nodes (holds objects that are directly linked to a dataset only)
    created = {}
    for obj in objects:
        parse_concepts(obj, created)

    for v in created.values():
        add_node(v['node'], s, g)


def add_direct_literals(literals, s, g):
    for l in literals:
        separated = [l[1]]
        if l[0] == 'keywordSet':
            # try split by comma and semicolon
            separated = l[1].replace(';', ',').split(',')

        p, lbl = get_relation(l[0])
        g.add((p, RDFS.label, Literal(lbl)))

        exactMatch = get_relation_existingvocab_match(l[0])
        if exactMatch:
            g.add((p, SKOS.exactMatch, exactMatch))

        closeMatch = get_relation_existingvocab_match(l[0], exactMatch=False)
        if closeMatch:
            g.add((p, SKOS.closeMatch, closeMatch))

        datatype = get_literal_type(l[0])
        for sep_l in separated:
            g.add((s, p, Literal(sep_l, datatype=datatype)))

    return g


def get_new_dataset(datasetid):
    dataset_uri = '{}dataset/{}'.format(bmo, datasetid)
    datasetid += 1

    return dataset_uri


def populate_dataset(datasetid, dataset, g):
    # add dataset instance
    s = rdflib.URIRef(get_new_dataset(datasetid))
    p = RDF.type
    o = bmo.Dataset
    g.add((s, p, o))
    g.add((o, SKOS.exactMatch, schema.Dataset))

    literals = [l for l in dataset if l[0] in supported_literals.keys()]
    objects = [l for l in dataset if l[0] not in supported_literals.keys()]

    g = add_direct_literals(literals, s, g)
    g = find_object_add_them(objects, s, g)


def run():
    datasetid = 0
    add_kg_metadata(g)
    for raw_dataset in load_solved_dataset():
        # for row in raw_dataset:
        # print(row)
        populate_dataset(datasetid, raw_dataset, g)
        datasetid += 1
        # break

    # g.serialize(destination="debug_BMKG.ttl", format="ttl", encoding="utf-8")
    # final export
    g.serialize(destination=join(results_root_path, "BMKG.ttl"), format="ttl", encoding="utf-8")
    g.serialize(destination=join(results_root_path, "BMKG.rdf"), format="pretty-xml", encoding="utf-8")
    g.serialize(destination=join(results_root_path, "BMKG.nt"), format="ntriples", encoding="utf-8")


if __name__ == '__main__':
    run()
