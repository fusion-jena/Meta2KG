from os import listdir, makedirs
from os.path import exists, join
import json
import flatdict
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


def init_clean(keys):
    clean_list = [k for k in keys if '@' not in k]
    return clean_list


def clean_keys(cleaned_list):
    """
    :param cleaned_list: list of dictionaries {'original': x key, 'value': flat value}
    :return:
    """
    keys = [item['original'] for item in cleaned_list]

    # #text and .para and .item inside each key, it has no further meaning
    useless_keywords = [
        '.#text', '.para', '.item',  # befchina
        'general.',  # bexis
        'OrganismLevelMetadata.', 'EnvironmentalLevelMetadata.', 'DatasetLevelMetadata.',
        'mstns:', 'Dataset.', 'SequenceLevelMetadata.',
        'DatasetType.', 'Data.',  # idiv
    ]
    # result_dict = {}
    for i, k in enumerate(keys):
        # result_dict[k] = {}
        clean = k
        for u_k in useless_keywords:
            clean = clean.replace(u_k, '')
        # result_dict[k].update({'clean': clean})
        cleaned_list[i]['clean'] = clean

    # mock original in clean
    mock_original = keys
    clean_list = keys
    try:
        while True:
            # try split by '.' and ':'
            general_word = get_top_level_keyword(clean_list)
            if is_repeated(general_word, clean_list):

                # remove it for the recursive cleaning
                clean_list = remove_word(general_word, clean_list)
                # remove it from the desired dictionary
                # [result_dict[k].update({'clean': result_dict[k]['clean'].replace(general_word, '')}) for k in mock_original]
                for i, k in enumerate(mock_original):
                    cleaned_list[i]['clean'] = cleaned_list[i]['clean'].replace(general_word, '')
            else:
                break
    except Exception as e:
        print(e)
    return cleaned_list


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    repos = listdir(unseen_final_json_path)
    keywords_dict = {}
    for repo in repos:
        repo_keywords = []

        meta_files_path = join(unseen_final_json_path, repo)
        filenames = listdir(meta_files_path)

        for fi, filename in enumerate(filenames):
            try:
                with open(join(meta_files_path, filename), 'r', encoding='utf-8') as file:
                    meta_dict = json.load(file)
                original_keys_list = [k for k in meta_dict.keys()]
                clean_keys_list = init_clean(original_keys_list)

                # initialize the clean_dict
                cleaned_dict = []
                # fill in values
                [cleaned_dict.append({'value': meta_dict[k], 'original': k}) for k in clean_keys_list]
                print(len(cleaned_dict))

                # get keys with list values
                list_dict = []
                [list_dict.append(item)
                 for item in cleaned_dict if isinstance(item['value'], list)]

                # simplify these lists into long str
                for item in list_dict:
                    v = item['value']
                    parent_key = item['original']

                    # value is a list of dictionary as well or just simple strings
                    if isinstance(v[0], str):
                        # this is a simple concatenation string in place manupliation
                        new_value = ', '.join(v)
                        for i, c_item in enumerate(cleaned_dict):
                            if c_item['original'] == parent_key:
                                cleaned_dict[i]['value'] = new_value
                                break

                    elif isinstance(v[0], dict):
                        try:
                            # further expansion is required here
                            for i, current_v in enumerate(v):
                                falltened_dict = dict(flatdict.FlatDict(current_v, delimiter='.'))

                                # keys to be replaced
                                old_keys = list(falltened_dict.keys())

                                # normalize the new value to be assigned to the new keys
                                for f_k in old_keys:
                                    if isinstance(falltened_dict[f_k], str):
                                        new_value = falltened_dict[f_k]
                                    elif isinstance(falltened_dict[f_k], list):
                                        # simple concatenation of list of strings
                                        new_value = ', '.join(falltened_dict[f_k])
                                    else:
                                        # keep the original value as is if it is a simple value (most expected)
                                        new_value = falltened_dict[f_k]

                                    falltened_dict[parent_key + '.' + f_k + '_' + str(i)] = new_value
                                    del falltened_dict[f_k]
                                # print(falltened_dict)
                                # add each key of the new flattened dict to the cleaned_dict
                                for f_k, f_v in falltened_dict.items():
                                    cleaned_dict.append({'original': f_k, 'value': f_v})
                        except Exception as e:
                            print(e)
                        # remove complex parent node:
                        [cleaned_dict.remove(c_item) for c_item in cleaned_dict if c_item['original'] == parent_key]

                    else:
                        print('Not supported type: {}'.format(type(v[0])))

                keywords_dict[filename] = clean_keys(cleaned_dict)

            except Exception as e:
                # print(e)
                # print(falltened_dict)
                # print(repo + ' ' + filename)
                continue

            transformed_keys_path = join(results_root_path, 'transformed_keys_values', repo)
            if not exists(transformed_keys_path):
                makedirs(transformed_keys_path)
            with open(join(transformed_keys_path, 'key_value_{}.json'.format(fi)), 'w', encoding='utf-8') as file:
                json.dump(keywords_dict, file, indent=4)
