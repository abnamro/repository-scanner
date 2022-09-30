# Standard Library
from functools import reduce
from typing import List


def remap_dict_keys(input_dict: dict, transformation_map: List):
    new_keys = [val[1] for val in transformation_map]
    for old_key, new_key in transformation_map:
        create_nested_dictionary(input_dict, new_key,  get_value_from_nested_dictionary(input_dict, *old_key))

    output_dict = {k: v for k, v in input_dict.items() if k in [key[0] for key in new_keys]}

    return output_dict


def create_nested_dictionary(dictionary, keys, value):
    for key in keys[:-1]:
        dictionary = dictionary.setdefault(key, {})
    if not isinstance(dictionary, dict):
        dictionary = {}
        dictionary = dictionary.setdefault(keys[-1], {})
    dictionary[keys[-1]] = value


def get_value_from_nested_dictionary(dictionary, *keys):
    return reduce(lambda d, key: d.get(key) if d else None, keys, dictionary)


def delete_keys_from_nested_dict(dict_del, lst_keys):
    if not lst_keys:
        return
    if len(lst_keys) == 1:
        del dict_del[lst_keys[0]]
    else:
        for value in dict_del.values():
            if isinstance(value, dict):
                delete_keys_from_nested_dict(value, lst_keys[1:])
