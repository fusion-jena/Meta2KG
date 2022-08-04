from os import makedirs
from os.path import exists, realpath, join

results_root_path = join(realpath('.'), 'results')

seen_meta_files_path = join(realpath('.'), 'meta_files')
seen_original_json_path = join(realpath('.'), 'results', 'original_json')
seen_normalized_json_path = join(realpath('.'), 'results', 'normalized_json')
seen_final_json_path = join(results_root_path, 'final_json')

pretrained_fasttext_path = join(realpath('.'), 'pre-trained-fasttext')
trained_model_path = join(results_root_path, 'trained_model')
if not exists(trained_model_path):
    makedirs(trained_model_path)