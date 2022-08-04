from os import listdir, makedirs
from os.path import exists, realpath, join

results_root_path = join(realpath('.'), 'results')


pretrained_fasttext_path = join(realpath('.'), 'pre-trained-fasttext')
trained_model_path = join(results_root_path, 'trained_model')

unseen_meta_files_path = join(realpath('.'), 'unseen_data')
unseen_original_json_path = join(realpath('.'), 'results', 'original_json')
unseen_normalized_json_path = join(realpath('.'), 'results', 'normalized_json')
unseen_final_json_path = join(realpath('.'), 'results', 'final_json')


# used for conditional loading of the model
use_wiki_embeddings = True
exp = 'weighted_mean' # 'keys_only' 'weighted_mean' 'mean'

# we use weighted embeddings for weighted_mean exp only ... DO NOT change
use_weighted_embeddings = False
if exp == 'weighted_mean':
    use_weighted_embeddings = True


# embedding path conditional loading
if use_wiki_embeddings:
    e_path = join(realpath('..'), 'results', 'ontoE', exp, 'ontokeys_wiki_embeddings.json')
else:
    e_path = join(realpath('..'), 'results', 'ontoE', exp, 'ontokeys_embeddings.json')


# two sources locations of the embeddings the pre-trained wiki-based and our custom
pretrained_path = join(realpath('..'), 'pre-trained-fasttext', 'wiki.en.bin')
custom_embedding_path = join(realpath('..'), 'trained_model', 'trained_fasttext.bin')

# where to store the solutions aka Matching results.
solved_path = join(realpath('.'), 'results', 'solved')
if not exists(solved_path):
    makedirs(solved_path)