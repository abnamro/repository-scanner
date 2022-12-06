# Standard Library
import unittest

# First Party
from resc_backend.resc_web_service.helpers.rule import (
    create_allow_list_dictionary,
    create_rule_dictionary,
    get_mapped_global_allow_list_obj,
    map_dictionary_to_rule_allow_list_object
)
from resc_backend.resc_web_service.schema.rule import Rule
from resc_backend.resc_web_service.schema.rule_allow_list import RuleAllowList


class TestRule(unittest.TestCase):
    def setUp(self):
        self.rule_list = []
        for i in range(1, 6):
            self.rule_list.append(Rule(
                rule_name=f"rule_name_{i}",
                description=f"description_{i}",
                tags=f"tags_{i}",
                entropy=1.1,
                secret_group=i,
                regex=f"regex_{i}",
                path=f"path_{i}",
                keywords=f"keywords_{i}"))

        self.allow_list = []
        for i in range(1, 6):
            self.allow_list.append(RuleAllowList(
                description=f"description_{i}",
                regexes=f"regexes_{i}",
                paths=f"paths_{i}",
                commits=f"commits_{i}",
                stop_words=f"stop_words_{i}"))

    def test_create_allow_list_dictionary(self):
        allow_list_obj = self.allow_list[0]
        allow_list_dict = create_allow_list_dictionary(allow_list=allow_list_obj)
        assert allow_list_dict["description"] == allow_list_obj.description
        assert allow_list_dict["regexes"] == allow_list_obj.regexes
        assert allow_list_dict["paths"] == allow_list_obj.paths
        assert allow_list_dict["commits"] == allow_list_obj.commits
        assert allow_list_dict["stop_words"] == allow_list_obj.stop_words

    def test_create_rule_dictionary(self):
        rule = self.rule_list[0]
        allow_list_dict = {"description": "dummy_desc", "regexes": "dummy_regexes", "paths": "dummy_paths",
                           "stop_words": "dummy_stop_words"}
        rule_dict = create_rule_dictionary(rule, allow_list_dict)
        assert rule_dict["id"] == rule.rule_name
        assert rule_dict["description"] == rule.rule_name
        assert rule_dict["tags"] == rule.tags
        assert rule_dict["entropy"] == rule.entropy
        assert rule_dict["secret_group"] == rule.secret_group
        assert rule_dict["regex"] == rule.regex
        assert rule_dict["path"] == rule.path
        assert rule_dict["keywords"] == rule.keywords
        assert rule_dict["allow_list"] == allow_list_dict

    def test_get_mapped_global_allow_list_obj(self):
        global_allow_list_dict = {"description": "dummy_desc", "regexes": "dummy_regexes", "paths": "dummy_paths",
                                  "stop_words": "dummy_stop_words"}
        toml_rule_dictionary = {"allowlist": global_allow_list_dict}
        global_allow_list_obj = get_mapped_global_allow_list_obj(toml_rule_dictionary)
        assert global_allow_list_obj is not None
        assert global_allow_list_obj.description == "dummy_desc"

    def test_map_dictionary_to_rule_allow_list_object(self):
        allow_list_dict = {"description": "dummy_desc", "regexes": "dummy_regexes", "paths": "dummy_paths",
                           "stop_words": "dummy_stop_words"}
        rule_allow_list = map_dictionary_to_rule_allow_list_object(allow_list_dict)

        assert rule_allow_list is not None
        assert rule_allow_list.description == "dummy_desc"
