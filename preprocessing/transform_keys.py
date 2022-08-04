from os import listdir
from os.path import join
import json
from config import seen_final_json_path, results_root_path


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

    # #text and .para and .item inside each key, it has no further meaning
    useless_keywords = [
        '.#text', '.para', '.item',  # befchina
        'general.',  # bexis
        'OrganismLevel', 'EnvironmentalLevel', 'DatasetLevel',
        'mstns:', 'Dataset.', 'SequenceLevelMetadata.',
        'DatasetType.', 'Data.',  # idiv
    ]
    for u_k in useless_keywords:
        clean_list = [k.replace(u_k, '') for k in clean_list]

    # print(clean_list)
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
    repos_path = seen_final_json_path
    repos = listdir(repos_path)
    keywords_dict = {}
    for repo in repos:
        repo_keywords = []

        meta_files_path = join(repos_path, repo)
        filenames = listdir(meta_files_path)

        for filename in filenames:
            try:
                with open(join(meta_files_path, filename), 'r', encoding='utf-8') as file:
                    meta_dict = json.load(file)
                original_keys_list = [k for k in meta_dict.keys()]
                cleaned_keys_list = clean_keys(original_keys_list)
                repo_keywords.extend(cleaned_keys_list)
            except Exception as e:
                print(e)
                print(repo + ' ' + filename)
                continue
        keywords_dict[repo] = sorted(list(set(repo_keywords)))

    with open(join(results_root_path, 'transformed_keywords.json'), 'w', encoding='utf-8') as file:
        json.dump(keywords_dict, file, indent=4)
