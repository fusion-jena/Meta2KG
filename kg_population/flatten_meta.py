from os import listdir, makedirs
from os.path import exists, join
import json
import xmltodict
import pandas as pd
from config import unseen_final_json_path, unseen_original_json_path, unseen_normalized_json_path, \
    unseen_meta_files_path

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repos = listdir(unseen_meta_files_path)
    for repo in repos:
        unseen_meta_files_path = join(unseen_meta_files_path, repo)
        unseen_original_json_path = join(unseen_original_json_path, repo)
        unseen_normalized_json_path = join(unseen_normalized_json_path, repo)
        unseen_final_json_path = join(unseen_final_json_path, repo)

        if not exists(unseen_normalized_json_path):
            makedirs(unseen_normalized_json_path)

            if not exists(unseen_final_json_path):
                makedirs(unseen_final_json_path)

            if not exists(unseen_original_json_path):
                makedirs(unseen_original_json_path)

        filenames = listdir(unseen_meta_files_path)

        for filename in filenames:
            try:
                with open(join(unseen_meta_files_path, filename), 'r', encoding='utf-8') as myfile:
                    obj = xmltodict.parse(myfile.read())

                # original json converted from XML
                with open(join(unseen_original_json_path, filename + '.json'), 'w') as file:
                    json.dump(obj[[_ for _ in obj.keys()][0]], file, indent=4)

                # Flatten keys till the forth level
                df = pd.json_normalize(obj[[_ for _ in obj.keys()][0]], max_level=7)
                df.to_json(join(unseen_normalized_json_path, filename + '_normalized.json'), indent=4)

                with open(join(unseen_normalized_json_path, filename + '_normalized.json'), 'r',
                          encoding='utf-8') as file:
                    normalized_json = json.load(file)

                # fix value formatting
                final_json = {}
                for key, value in normalized_json.items():
                    final_json[key] = [v for v in value.values()][0]

                # save final normalized json file
                with open(join(unseen_final_json_path, filename + '_final.json'), 'w') as file:
                    json.dump(final_json, file, indent=4)
            except Exception as e:
                print(e)
                print(repo + ' ' + filename)
                continue
