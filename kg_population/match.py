import csv
from os.path import join
from os import listdir
import numpy as np
from gensim.models import FastText
from gensim.models.fasttext import load_facebook_model
import json
from numpy import dot
from numpy.linalg import norm
from collections import OrderedDict
from config import e_path, use_wiki_embeddings, use_weighted_embeddings, results_root_path \
    , pretrained_path, pretrained_fasttext_path, solved_path


# fastest solution of cosine sim based on only numpy
def calculate_cosine_sim(a, b):
    cos_sim = dot(a, b) / (norm(a) * norm(b))
    return cos_sim


def load_ontokeys_embeddings():
    with open(e_path, 'r') as file:
        ontokeys_dict = json.load(fp=file)
    return ontokeys_dict


def load_model():
    # conditional loading of the onto embeddings
    if use_wiki_embeddings:
        # facebook pre-trained model
        model = load_facebook_model(pretrained_fasttext_path)
    else:
        # our trained model
        model = FastText.load(pretrained_path)

    return model


def get_embedding(sample, model):
    confusing_words = ['north', 'east', 'south', 'west',
                       'numberOfGP', 'numberOfEP', 'numberOfMIP', 'numberOfVIP',
                       'numberOf', 'doi',
                       'givenName', 'surName',
                       ]
    for cw in confusing_words:
        if cw in sample:
            last_word = sample.split('.')[len(sample.split('.')) - 1]
            sample = last_word
            break
    # we construct the embedding of testing data the same way of the training data.
    # Puts much emphasize on last distinct part of the word.
    e = [0 for _ in range(model.vector_size)]
    if use_weighted_embeddings:
        dSubWords = sample.split('.')
        for i, dsw in enumerate(dSubWords):
            e += model.wv[dsw] * (i + 1)
        e /= len(dSubWords)
    else:
        e += model.wv[sample]

    return e


def get_testing_key_value():
    transformed_keys_path = join(results_root_path, 'transformed_keys_values')
    filenames = []
    for repo in listdir(transformed_keys_path):
        filenames.extend([join(transformed_keys_path, repo, f) for f in listdir(join(transformed_keys_path, repo))])
    content_lst = []
    for f in filenames:
        with open(f, 'r') as file:
            content_lst += [json.load(file)]

    return content_lst


def calculate_sim(ontokeys_dict, test_embed):
    sim = OrderedDict()
    for k, v in ontokeys_dict.items():
        sim_value = calculate_cosine_sim(np.array(v), np.array(test_embed))
        # TODO: tune this threshold if needed
        if sim_value > 0.7:
            sim[k] = sim_value

    # highest similarity goes first
    sim_descending = OrderedDict(sorted(sim.items(),
                                        key=lambda kv: kv[1], reverse=True)[:1])

    return sim_descending


def calculate_sim_for_all(ontokeys_dict, test_files, model):
    mapped = {}
    for dataset in test_files:
        for fi, vals in enumerate(dataset.values()):
            lines = []
            # append a header line
            lines.append(['Score', 'Prediction', 'Metadata Key', 'Metadata Value'])
            for v in vals:
                if v['clean'] in mapped.keys():
                    # retrieve calculated embedding
                    meta_key_e = mapped[v['clean']]
                else:
                    meta_key_e = get_embedding(v['clean'], model)
                    mapped.update({v['clean']: meta_key_e})

                meta_value = v['value']
                sim_dict = calculate_sim(ontokeys_dict, meta_key_e)
                if not sim_dict:
                    lines.append([-1, 'Not Mapped', v['clean'], meta_value])
                for mapped_onto_key, sim in sim_dict.items():
                    lines.append([round(sim, 3), mapped_onto_key, v['clean'], meta_value])
            # save lines to a separate csv per repo
            with open(join(solved_path, '{}_solutions.csv'.format(fi)), 'w', newline='',
                      encoding='utf-8', errors='ignore') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer.writerows(lines)


def test(model):
    # test_sample = 'additionalMetadata.metadata.gbif.citation' # mock what we will get from the flatten and cleaning.
    # test_sample = 'contacts.email'  # mock what we will get from the flatten and cleaning.
    test_sample = ['coverage.geographicCoverage.boundingCoordinates.northBoundingCoordinate', 'northBoundingCoordinate']
    for t in test_sample:
        test_embed = get_embedding(t, model)
        similarity = calculate_sim(ontokeys_dict, test_embed)
        print(t)
        for k, v in similarity.items():
            print('{} \t: {}'.format(k, v))
        print("====================")


if __name__ == '__main__':
    ontokeys_dict = load_ontokeys_embeddings()
    model = load_model()
    # test(model)
    test_dict = get_testing_key_value()
    calculate_sim_for_all(ontokeys_dict, test_dict, model)
