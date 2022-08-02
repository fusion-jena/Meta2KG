from os import listdir, makedirs
from os.path import exists, realpath, join
import json
import xmltodict
import pandas as pd
from config import seen_meta_files_path, seen_final_json_path, seen_original_json_path, seen_normalized_json_path

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repos = listdir(seen_meta_files_path)
    for repo in repos:
        seen_meta_files_path = join(seen_meta_files_path, repo)
        seen_original_json_path = join(seen_original_json_path, repo)
        seen_normalized_json_path = join(seen_normalized_json_path, repo)
        seen_final_json_path = join(seen_final_json_path, repo)

        if not exists(seen_normalized_json_path):
            makedirs(seen_normalized_json_path)

            if not exists(seen_final_json_path):
                makedirs(seen_final_json_path)

            if not exists(seen_original_json_path):
                makedirs(seen_original_json_path)

        filenames = listdir(seen_meta_files_path)

        for filename in filenames:
            try:
                with open(join(seen_meta_files_path, filename), 'r', encoding='utf-8') as myfile:
                    obj = xmltodict.parse(myfile.read())

                # original json converted from XML
                with open(join(seen_original_json_path, filename + '.json'), 'w') as file:
                    json.dump(obj[[_ for _ in obj.keys()][0]], file, indent=4)

                # Flatten keys till the forth level
                df = pd.json_normalize(obj[[_ for _ in obj.keys()][0]], max_level=7)
                df.to_json(join(seen_normalized_json_path, filename + '_normalized.json'), indent=4)

                with open(join(seen_normalized_json_path, filename + '_normalized.json'), 'r', encoding='utf-8') as file:
                    normalized_json = json.load(file)

                # fix value formatting
                final_json = {}
                for key, value in normalized_json.items():
                    final_json[key] = [v for v in value.values()][0]

                # save final normalized json file
                with open(join(seen_final_json_path, filename + '_final.json'), 'w') as file:
                    json.dump(final_json, file, indent=4)
            except Exception as e:
                print(e)
                print(repo + ' ' + filename)
                continue