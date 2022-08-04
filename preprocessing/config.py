from os.path import realpath, join

results_root_path = join(realpath('.'), 'results')

seen_meta_files_path = join(realpath('.'), 'meta_files')
seen_original_json_path = join(realpath('.'), 'results', 'original_json')
seen_normalized_json_path = join(realpath('.'), 'results', 'normalized_json')
seen_final_json_path = join(results_root_path, 'final_json')