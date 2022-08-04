import json
from os.path import realpath, join
from os import listdir
import pandas as pd
from rdflib import Literal
from rdflib.namespace import RDF

from utils.mappings import *
from utils.namespaces import *
from utils.data_structure import MyNode, MyLiteral
from random import seed, randint
from validate_values import validate

seed(1)


def load_solved_dataset():
    # loads the solved datasets one by one
    solved_path = join(realpath('.'), 'results', 'solved')
    files = listdir(solved_path)
    for f in files[0:]:
        df = pd.read_csv(join(solved_path, f), header=0)
        mapping = []
        for p, v in zip(df['Prediction'].tolist(), df['Metadata Value'].tolist()):
            if p != 'Not Mapped':
                if validate.is_valid(v, p):
                    mapping.append((p, v))
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
    g.add((s, p, o))
    if node.literals:
        for l in node.literals:
            p_l, lbl = get_relation(l.name)
            g.add((p_l, RDFS.label, Literal(lbl)))
            g.add((o, p_l, Literal(l.value, datatype=l.datatype)))
    if node.members:
        for child in node.members:
            return add_node(child, o, g)


def parse_concepts(obj, parent, created):
    levels = obj[0].split('_')

    leaf = '.'.join(levels)
    if leaf in created:
        created[leaf]['freq'] += 1
    else:
        created[leaf] = {'name': leaf, 'freq': 1, 'is_leaf': True, 'imports': []}

    current = leaf
    for ii in range(len(levels) - 1, 0, -1):
        node = '.'.join(levels[0:ii])
        if node in created:
            created[node]['freq'] += 1
        else:
            created[node] = {'name': node, 'freq': 1, 'is_leaf': False, 'imports': []}
        created[node]['imports'] += [current]
        current = node


def find_object_add_them(objects, parent, created):
    for obj in objects:
        parse_concepts(obj, parent, created)


def add_direct_literals(literals, parent, created):
    for l in literals:
        if l[0] == 'keywordSet':
            # try split by comman and semincolon
            seprated = l[1].replace(';', ',').split(',')
        else:
            seprated = [l[1]]

        litName = 'literal.' + l[0]
        for _ in seprated:
            if litName in created:
                created[litName]['freq'] += 1
            else:
                created[litName] = {'name': litName, 'freq': 1, 'is_leaf': True, 'imports': []}

    return g


def populate_dataset(dataset, g, created):
    parent = "Dataset"
    literals = [l for l in dataset if l[0] in supported_literals.keys()]
    objects = [l for l in dataset if l[0] not in supported_literals.keys()]

    g = add_direct_literals(literals, parent, created)
    g = find_object_add_them(objects, parent, created)


if __name__ == '__main__':

    # my created root nodes (holds objects that are directly linked to a dataset only)
    created = {}
    for raw_dataset in load_solved_dataset():
        # print(raw_dataset)
        populate_dataset(raw_dataset, g, created)
        # break

    for k, v in created.items():
        # keep unique only
        v["imports"] = list(set(v["imports"]))
        for idx, i in enumerate(v["imports"]):
            if not created[i]['is_leaf']:
                last_part = i.split('.')[len(i.split('.')) - 1]
                v["imports"][idx] = i + '.' + str(last_part[0]).upper() + last_part[1:]
        if not v['is_leaf']:
            last_part = v['name'].split('.')[len(v['name'].split('.')) - 1]
            v['name'] = v['name'] + '.' + str(last_part[0]).upper() + last_part[1:]

    # assign firstLevel to dataset
    firstLevel = []
    dataset_freq = 0
    for k, v in created.items():
        if len(k.split('.')) == 1 or 'literal' in k:
            dataset_freq += v["freq"]
            firstLevel += [v["name"]]

    created["dataset"] = {"name": "Dataset", "freq": dataset_freq, "imports": firstLevel}

    # adding root
    for v in created.values():
        for idx, i in enumerate(v["imports"]):
            v["imports"][idx] = 'root.' + v["imports"][idx]
        v['name'] = 'root.' + v['name']

    obj = list(created.values())
    with open("BMKG_flare.json", "w") as file:
        json.dump(obj, file, indent=4)
