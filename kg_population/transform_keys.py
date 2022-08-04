from os import listdir, makedirs
from os.path import exists, join
import json
from config import unseen_final_json_path, results_root_path


def is_repeated(word, lst):
    cnt = 0
    for w in lst:
        if word in w:
            cnt += 1
    return cnt >= 0.4 * (len(lst))


def remove_word(word, lst):
    return [w.replace(word, '') for w in lst]


def get_top_level_keyword(lst):
    sep = '.'
    parts = lst[0].split(sep)
    if len(parts) == 1:
        sep = ':'
        parts = lst[0].split(sep)
    general_word = parts[0] + sep
    return general_word


def clean_keys(keys):
    # exclude keywords that has @id, @type ... etc (less meaningful format)
    clean_list = [k for k in keys if '@' not in k]

    useless_keywords = [
        '.#text', '.para', '.item',  # befchina
        'general.',  # bexis
        'OrganismLevelMetadata.', 'EnvironmentalLevelMetadata.', 'DatasetLevelMetadata.',
        'mstns:', 'Dataset.', 'SequenceLevelMetadata.',
        'DatasetType.', 'Data.',  # idiv
    ]

    for u_k in useless_keywords:
        clean_list = [k.replace(u_k, '') for k in clean_list]

    try:
        while True:
            # try split by '.' and ':'
            general_word = get_top_level_keyword(clean_list)
            if is_repeated(general_word, clean_list):
                # remove it
                clean_list = remove_word(general_word, clean_list)
            else:
                break
    except Exception as e:
        clean_list = keys
    return clean_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repos = listdir(unseen_final_json_path)
    keywords_dict = {}
    for repo in repos:
        repo_keywords = []

        meta_files_path = join(unseen_final_json_path, repo)
        filenames = listdir(meta_files_path)

        for i, filename in enumerate(filenames):
            try:
                with open(join(meta_files_path, filename), 'r', encoding='utf-8') as file:
                    meta_dict = json.load(file)
                original_keys_list = [k for k in meta_dict.keys()]
                cleaned_keys_list = clean_keys(original_keys_list)
            except Exception as e:
                print(e)
                print(repo + ' ' + filename)
                continue
            keywords_dict[filename] = sorted(list(set(cleaned_keys_list)))

            transformed_keys_path = join(results_root_path, 'transformed_keys', repo)
            if not exists(transformed_keys_path):
                makedirs(transformed_keys_path)
            with open(join(transformed_keys_path, 'transformed_keywords_{}.json'.format(i)), 'w',
                      encoding='utf-8') as file:
                json.dump(keywords_dict, file, indent=4)
