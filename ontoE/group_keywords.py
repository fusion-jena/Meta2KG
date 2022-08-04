import csv
from os.path import join
import json
from config import results_root_path

# these are derived from the target ontology to limit the search scope.
# core = ['version', 'identi', 'lang', 'intellectua', 'description', 'cit', 'doi', 'format', 'keyword',
#         'title', 'abstract', 'license',
#
#         'west', 'east', 'south', 'north',
#         'OfEP', 'OfGP', 'OfVIP', 'OfMIP',
#         'rank', 'common',
#         'taxon', 'tempor', 'geog', 'date',
#
#         'countr', 'city', 'postal', 'street', 'delivery', 'addr'  # addr related
#
#                                                           'owner', 'author', 'contact', 'provider', 'creator',
#         # persons
#         'organiza', 'role',
#
#         'simple', 'measure', 'introduction', 'equipment',
#         'method',
#
#         'project', 'fund']


core = ['curator', 'collector', 'leader']


def get_keywords():
    with open(join(results_root_path, 'transformed_keywords.json')) as file:
        content = json.load(file)
    keywords = []
    for val in content.values():
        keywords.extend(val)

    print(len(keywords))
    return keywords


def get_keywords_from_instances():
    with open(join(results_root_path, 'transformed_keywords_values.json')) as file:
        content = json.load(file)
    keywords = []
    for val in content.values():
        for vi in val:
            keywords += [vi['clean']]

    print(len(keywords))
    return keywords


def group_keywords(keywords):
    print('work on only unique keywords')
    keywords = list(set(keywords))

    added = []
    grouped_dict = {}
    for core_w in core:
        matched = [w for w in keywords if core_w.lower() in w.lower() and w not in added]
        added.extend(matched)
        grouped_dict.update({core_w: matched})
    return grouped_dict


def get_frequencies(keywords, grouped_keywords):
    keywords = [w.lower() for w in keywords]
    freq = {}

    for k, v in grouped_keywords.items():
        freq[k] = {}
        for vi in v:
            freq[k][vi] = 0
            for keyword in keywords:
                if vi.lower() in keyword.lower():
                    freq[k][vi] += 1

    for k, v in freq.items():
        print(k)
        print('-----')
        for ki, vi in v.items():
            print('\t\t{}: {}\n'.format(ki, vi))
        print('====================')
    return freq


def store_frequencies(freq_dict):
    lines = []
    for cor_k, vals in freq_dict.items():
        for word, freq in vals.items():
            lines.append([cor_k, word, freq])
    with open(join(results_root_path, 'keywords_freq.csv'), 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(lines)


## for exploration only ... instead of manual inspection
def get_keyword_from_instances(keyword):
    with open(join(results_root_path, 'transformed_keywords_values.json')) as file:
        content = json.load(file)
    keywords = []
    for val in content.values():
        for vi in val:
            if keyword.lower() in vi['clean'].lower():
                keywords += [vi['clean']]

    keywords = list(set(keywords))
    keywords.sort()
    for k in keywords:
        print(k)


if __name__ == '__main__':
    keywords = get_keywords()
    grouped_dict = group_keywords(keywords)
    for k, v in grouped_dict.items():
        print(k)
        print('-----')
        for vi in v:
            print('\t\t{}\n'.format(vi))
        print('====================')
    keywords = get_keywords_from_instances()
    freq_dict = get_frequencies(keywords, grouped_dict)
    store_frequencies(freq_dict)
    ## for exploration only ... instead of manual inspection
    # get_keyword_from_instances('metadataProvider')
