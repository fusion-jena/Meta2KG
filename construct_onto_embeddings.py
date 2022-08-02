from os.path import join
from gensim.models import FastText
from gensim.models.fasttext import load_facebook_model
import json
import pandas as pd
from config import results_root_path, trained_model_path, pretrained_fasttext_path

# used for conditional loading of the model
use_wiki_embeddings = False

# some of the key have negative examples, if True it will add them to the final embedding with negative weight.
process_negative_samples = False

# weighted embeddings calculations of the nested words, highest weight goes to the last word (most distinct)
use_weighted_embeddings = False

# if True, it will process the ontological key as a whole input only,
# it will ignore the relevant keys (no mean calculation)
use_keys_only = False


def get_mapping_dict():
    df = pd.read_csv(join(results_root_path, 'onto_keywords_mapping.csv'), header=0)
    df = df.fillna('')
    length = len(df)

    # initialize empty mapping dictionary with unique ontoKeys
    mapping_dict = {}
    [mapping_dict.update({oK: {'positive': [], 'negative': []}}) for oK in set(df['OntoKey'].tolist())]

    for i in range(length):
        mapping_dict[df['OntoKey'][i]]['positive'] += [df['Keyword'][i]]
        if df['Negative Examples'][i]:
            mapping_dict[df['OntoKey'][i]]['negative'] += [df['Negative Examples'][i]]

    for k, vals in mapping_dict.items():
        print(k)
        print('----')
        for ki, v in vals.items():
            print('\t\t{}\n'.format(ki))
            for vi in v:
                print('\t\t\t{}\n'.format(vi))
        print('=====================================')

    return mapping_dict


def load_model():
    if use_wiki_embeddings:
        # facebook pre-trained model
        model = load_facebook_model(join(pretrained_fasttext_path, 'wiki.en.bin'))
    else:
        # our trained model
        model = FastText.load(join(trained_model_path, 'trained_fasttext.bin'))
    return model


def get_embeddings_dict_for_keys_only(mapping_dict, model):
    E = {}

    # we try to split and apply weighting summation/avg as a function of the sub-word index
    for ontoKey, data_key in mapping_dict.items():
        E[ontoKey] = model.wv[ontoKey].tolist()
    return E


def get_embeddings_dict(mapping_dict, model):
    E = {}

    # we try to split and apply weighting summation/avg as a function of the sub-word index
    for ontoKey, data_key in mapping_dict.items():
        e = [0 for _ in range(model.vector_size)]
        word_n = len(data_key['positive'])
        for dK in data_key['positive']:
            if not dK:
                continue
            if use_weighted_embeddings:
                dSubWords = dK.split('.')
                for i, dsw in enumerate(dSubWords):
                    e += model.wv[dsw] * (i + 1)
            else:
                e += model.wv[dK]
        e /= word_n

        if process_negative_samples and data_key['negative']:
            n_e = [0 for _ in range(model.vector_size)]
            word_n = len(data_key['negative'])
            for n_dK in data_key['negative']:
                if use_weighted_embeddings:
                    dSubWords = n_dK.split('.')
                    for i, dsw in enumerate(dSubWords):
                        n_e += model.wv[dsw] * (-(i + 1))
                else:
                    n_e += model.wv[n_dK] * -1
            n_e /= word_n
            e += n_e

        E[ontoKey] = e.tolist()
    return E


if __name__ == '__main__':
    mapping_dict = get_mapping_dict()
    model = load_model()
    if use_keys_only:
        E = get_embeddings_dict_for_keys_only(mapping_dict, model)
    else:
        E = get_embeddings_dict(mapping_dict, model)

    if use_wiki_embeddings:
        e_path = join(results_root_path, 'ontokeys_wiki_embeddings.json')
    else:
        e_path = join(results_root_path, 'ontokeys_embeddings.json')

    with open(e_path, 'w') as file:
        json.dump(E, fp=file, indent=4)
