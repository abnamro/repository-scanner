# First Party
from resc_backend.helpers.dict_remapper import (
    create_nested_dictionary,
    delete_keys_from_nested_dict,
    get_value_from_nested_dictionary,
    remap_dict_keys
)


def test_remap_dict_keys():
    input_dict = {"a": 1, "b": 2}
    expected_output_dict = {"a1": 1, "c": 2}
    remapping_dict = [[["a"], ["a1"]], [["b"], ["c"]]]
    output_dict = remap_dict_keys(input_dict, remapping_dict)
    assert output_dict == expected_output_dict


def test_nested_input_remap_dict_keys():
    input_dict = {"a": {"a1": 1}, "b": 2}
    expected_output_dict = {"a1": 1, "c": 2}
    remapping_dict = [[["a", "a1"], ["a1"]], [["b"], ["c"]]]
    output_dict = remap_dict_keys(input_dict, remapping_dict)
    assert output_dict == expected_output_dict


def test_nested_output_remap_dict_keys():
    input_dict = {"a": 1, "b": 2}
    expected_output_dict = {"w": {"a1": 1}, "c": 2}
    remapping_dict = [[["a"], ["w", "a1"]], [["b"], ["c"]]]
    output_dict = remap_dict_keys(input_dict, remapping_dict)
    assert output_dict == expected_output_dict


def test_no_remap_dict_keys():
    input_dict = {"a": 1, "b": 2}
    expected_output_dict = {}
    remapping_dict = []
    output_dict = remap_dict_keys(input_dict, remapping_dict)
    assert output_dict == expected_output_dict


def test_create_nested_dictionary():

    keys = ["a", "b", "c"]
    value = "abc"
    expected_output_dict = {"a": {"b": {"c": "abc"}}}
    nested_dict = {}
    create_nested_dictionary(nested_dict, keys, value)
    assert nested_dict == expected_output_dict


def test_get_value_from_nested_dictionary():
    nested_dict = {"a": {"b": {"c": "abc"}}}
    keys = ["a", "b", "c"]
    assert get_value_from_nested_dictionary(nested_dict, *keys) == "abc"


def test_delete_keys_from_nested_dict():
    nested_dict = {"a": {"b": {"c": "abc"}}}
    keys = ["a", "b", "c"]
    expected_dict = {"a": {"b": {}}}
    delete_keys_from_nested_dict(nested_dict, keys)
    assert nested_dict == expected_dict
