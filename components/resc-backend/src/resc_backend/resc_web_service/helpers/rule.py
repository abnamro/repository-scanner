# pylint: disable=R0912
# Standard Library
import logging
import os
import re
from typing import List

# Third Party
import tomlkit
from fastapi import File, HTTPException
from tomlkit import aot, comment, document, nl, table
from tomlkit.items import String, StringType

# First Party
from resc_backend.constants import ALLOWED_EXTENSION, TEMP_RULE_FILE, TOML_CUSTOM_DELIMITER
from resc_backend.resc_web_service.schema.rule import Rule
from resc_backend.resc_web_service.schema.rule_allow_list import RuleAllowList

FILE_NAME_REGEX = r"^[a-zA-Z0-9-_]+$"

logger = logging.getLogger(__name__)


def create_allow_list_dictionary(allow_list: RuleAllowList) -> dict:
    """
        Create a dictionary for allow list when an RuleAllowList object is supplied
    :param allow_list:
        RuleAllowList object
    :return: AllowList dictionary
        The output will contain a dictionary of AllowList
    """
    allow_list_dict = {}
    if allow_list:
        if allow_list.description:
            allow_list_dict["description"] = allow_list.description
        if allow_list.regexes:
            allow_list_dict["regexes"] = allow_list.regexes
        if allow_list.paths:
            allow_list_dict["paths"] = allow_list.paths
        if allow_list.commits:
            allow_list_dict["commits"] = allow_list.commits
        if allow_list.stop_words:
            allow_list_dict["stop_words"] = allow_list.stop_words
    return allow_list_dict


def create_rule_dictionary(rule: Rule, allow_list_dict: dict, tags: str) -> dict:
    """
        Create a dictionary for rule when Rule object and RuleAllowList dict are supplied
    :param rule:
        Rule object
    :param allow_list_dict:
        Allow list dictionary
    :param tags:
        String of tags of the rule
    :return: Rule dictionary
        The output will contain a dictionary of Rule
    """
    rule_dict = {}
    if rule.rule_name:
        rule_dict["id"] = rule.rule_name
        rule_dict["description"] = rule.rule_name
    if tags:
        rule_dict["tags"] = tags
    if rule.entropy:
        rule_dict["entropy"] = rule.entropy
    if rule.secret_group:
        rule_dict["secret_group"] = rule.secret_group
    if rule.regex:
        rule_dict["regex"] = rule.regex
    if rule.path:
        rule_dict["path"] = rule.path
    if rule.keywords:
        rule_dict["keywords"] = rule.keywords
    if allow_list_dict:
        rule_dict["allow_list"] = allow_list_dict
    return rule_dict


def create_toml_dictionary(rule_pack_version: str, rules: List[str], global_allow_list: List[str], rule_tag_names) \
        -> dict:
    """
        Create a dictionary for gitleaks toml rule for specified rule pack version, rules and global allow list
    :param rule_pack_version:
        Rule pack version
    :param rules:
        Rule list
    :param global_allow_list:
        Global Allow list
    :param rule_tag_names:
        List of rule names and tags
    :return: toml dictionary
        The output will contain a dictionary for gitleaks toml rule
    """
    rule_list = []
    for rule in rules:
        allow_list_dict = create_allow_list_dictionary(rule)
        tags_list = [x.name for x in rule_tag_names if x.rule_name == rule.rule_name]
        tags = None
        if len(tags_list) >= 1:
            tags = ','.join(tags_list)
        rule_dict = create_rule_dictionary(rule, allow_list_dict, tags)
        rule_list.append(rule_dict)

    global_allow_list_dict = create_allow_list_dictionary(global_allow_list)

    rule_toml_dict = {"title": "gitleaks config"}
    if rule_pack_version:
        rule_toml_dict["version"] = rule_pack_version
    if rule_list:
        rule_toml_dict["rules"] = rule_list
    if global_allow_list_dict:
        rule_toml_dict["allowlist"] = global_allow_list_dict
    return rule_toml_dict


def get_mapped_global_allow_list_obj(toml_rule_dictionary: dict) -> RuleAllowList:
    """
        Get global allow list object from toml rule dictionary
    :param toml_rule_dictionary:
        TOML rule dictionary
    :return: RuleAllowList
        The output will contain an object of RuleAllowList
    """
    global_allow_list_obj = None
    if "allowlist" in toml_rule_dictionary:
        global_allow_list = toml_rule_dictionary.get("allowlist")
        global_allow_list_obj = map_dictionary_to_rule_allow_list_object(global_allow_list)
    else:
        logger.info("No global allow list is present in the toml file!")
    return global_allow_list_obj


def map_dictionary_to_rule_allow_list_object(allow_list_dictionary: dict) -> RuleAllowList:
    """
        Convert allow list dictionary to RuleAllowList object
    :param allow_list_dictionary:
        AllowList dictionary
    :return: RuleAllowList
        The output will contain an object of RuleAllowList
    """
    rule_allow_list = None
    if allow_list_dictionary:
        description = allow_list_dictionary["description"] if "description" in allow_list_dictionary else None
        regexes = None
        paths = None
        commits = None
        stopwords = None

        if "regexes" in allow_list_dictionary:
            regexes = ""
            regexes_array = allow_list_dictionary["regexes"]
            for index, regex in enumerate(regexes_array):
                if index + 1 < len(regexes_array):
                    regexes += regex + TOML_CUSTOM_DELIMITER
                else:
                    regexes += regex

        if "paths" in allow_list_dictionary:
            paths = ""
            paths_array = allow_list_dictionary["paths"]
            for index, path in enumerate(paths_array):
                if index + 1 < len(paths_array):
                    paths += path + TOML_CUSTOM_DELIMITER
                else:
                    paths += path

        if "commits" in allow_list_dictionary:
            commits_array = allow_list_dictionary["commits"]
            commits = ",".join(commits_array)

        if "stopwords" in allow_list_dictionary:
            stopword_array = allow_list_dictionary["stopwords"]
            stopwords = ",".join(stopword_array)

        rule_allow_list = RuleAllowList(description=description, regexes=regexes,
                                        paths=paths, commits=commits, stop_words=stopwords)
    return rule_allow_list


def create_toml_rule_file(parsed_toml_dictionary: dict):
    """
        Create a TOML file from a dictionary
    :param parsed_toml_dictionary:
        TOML dictionary
    :return: toml_file
        Returns toml file
    """
    doc = document()
    doc.add(comment("This is a gitleaks configuration file."))
    doc.add(comment("Rules and allowlists are defined within this file."))
    doc.add(comment("Rules instruct gitleaks on what should be considered a secret."))
    doc.add(comment("Allowlists instruct gitleaks on what is allowed, i.e. not a secret."))
    doc.add(nl())

    if "title" in parsed_toml_dictionary:
        doc.add("title", parsed_toml_dictionary["title"])
    doc.add(nl())
    if "version" in parsed_toml_dictionary:
        doc.add("version", parsed_toml_dictionary["version"])
    doc.add(nl())

    # Global allow list table
    global_allow_list_table = create_allow_list_toml_table(input_dictionary=parsed_toml_dictionary, key="allowlist")
    if global_allow_list_table:
        doc.add('allowlist', global_allow_list_table)
        doc.add(nl())

    # Rules table
    rule_array_table = create_rule_array_toml_table(rule_dictionary=parsed_toml_dictionary)
    doc.add("rules", rule_array_table)

    toml_string = tomlkit.dumps(doc)
    with open(TEMP_RULE_FILE, "w", encoding="utf-8") as toml_file:
        toml_file.write(toml_string)
        toml_file.close()
    return toml_file


def get_multiline_array_for_toml_file(input_dictionary: dict, key: str, string_type: str,
                                      delimiter: str) -> tomlkit.array():
    """
        Create multiline toml array for the input dictionary value
    :param input_dictionary:
        Input dictionary
    :param key:
        key of Input dictionary
    :param string_type:
        Multi Line Literal or Single Line Basic
    :param delimiter:
        TOML_CUSTOM_DELIMITER or ","
    :return: tomlkit.array
        The output will return a toml array
    """
    multiline_array = tomlkit.array()
    array_from_db = input_dictionary[key].split(delimiter)
    for value_str in array_from_db:
        multiline_array.append(String.from_raw(String.from_raw(value_str), string_type))
        multiline_array.multiline(True)
    return multiline_array


def create_allow_list_toml_table(input_dictionary: dict, key: str) -> table():
    """
       Create a TOML table for rule allow list
   :param input_dictionary:
       AllowList dictionary
    :param key:
       Key in AllowList dictionary
   :return: table
       Returns allow list TOML table
   """
    allow_list_table = None
    if key in input_dictionary:
        allow_list_table = table()
        allow_list_dict = input_dictionary[key]
        if "description" in allow_list_dict:
            allow_list_table.add("description", allow_list_dict["description"])
        if "paths" in allow_list_dict:
            multiline_path_array = get_multiline_array_for_toml_file(input_dictionary=allow_list_dict,
                                                                     key="paths", string_type=StringType.MLL,
                                                                     delimiter=TOML_CUSTOM_DELIMITER)
            allow_list_table.add("paths", multiline_path_array)
        if "regexes" in allow_list_dict:
            multiline_regex_array = get_multiline_array_for_toml_file(input_dictionary=allow_list_dict,
                                                                      key="regexes", string_type=StringType.MLL,
                                                                      delimiter=TOML_CUSTOM_DELIMITER)
            allow_list_table.add("regexes", multiline_regex_array)
        if "commits" in allow_list_dict:
            multiline_commit_array = get_multiline_array_for_toml_file(input_dictionary=allow_list_dict,
                                                                       key="commits", string_type=StringType.SLB,
                                                                       delimiter=",")
            allow_list_table.add("commits", multiline_commit_array)
        if "stop_words" in allow_list_dict:
            multiline_stopword_array = get_multiline_array_for_toml_file(input_dictionary=allow_list_dict,
                                                                         key="stop_words", string_type=StringType.SLB,
                                                                         delimiter=",")
            allow_list_table.add("stopwords", multiline_stopword_array)
    return allow_list_table


def create_rule_array_toml_table(rule_dictionary: dict) -> aot():
    """
      Create an array of table for rule list
   :param rule_dictionary:
       Rule dictionary
   :return: table
       Return an array of table
   """

    # Rule Table
    rule_array_table = aot()
    if "rules" in rule_dictionary:
        for rule_dict in rule_dictionary["rules"]:
            rule_table = table()
            if "id" in rule_dict:
                rule_table.add("id", rule_dict["id"])
            if "description" in rule_dict:
                rule_table.add("description", rule_dict["description"])
            if "entropy" in rule_dict:
                rule_table.add("entropy", rule_dict["entropy"])
            if "secret_group" in rule_dict:
                rule_table.add("secretGroup", rule_dict["secret_group"])
            if "regex" in rule_dict:
                rule_table.add("regex", String.from_raw(rule_dict["regex"], StringType.MLL))
            if "path" in rule_dict:
                rule_table.add("path", String.from_raw(rule_dict["path"], StringType.MLL))
            if "tags" in rule_dict:
                multiline_tag_array = get_multiline_array_for_toml_file(input_dictionary=rule_dict,
                                                                        key="tags",
                                                                        string_type=StringType.SLB,
                                                                        delimiter=",")
                rule_table.add("tags", multiline_tag_array)
            if "keywords" in rule_dict:
                multiline_keyword_array = get_multiline_array_for_toml_file(input_dictionary=rule_dict,
                                                                            key="keywords",
                                                                            string_type=StringType.SLB,
                                                                            delimiter=",")
                rule_table.add("keywords", multiline_keyword_array)

            # Rule Allow List Table
            if "allow_list" in rule_dict:
                allow_list_table = create_allow_list_toml_table(input_dictionary=rule_dict, key="allow_list")
                rule_table.append('allowlist', allow_list_table)

            rule_array_table.append(rule_table)
    return rule_array_table


def validate_uploaded_file_and_read_content(rule_file: File) -> str:
    """
      Validate the uploaded file and read content
   :param rule_file:
       File uploaded
   :return: content
       Return file content
   """
    file_name = os.path.splitext(rule_file.filename)[0]

    # File name validation
    is_valid_file_name = bool(re.match(FILE_NAME_REGEX, file_name))
    if not is_valid_file_name:
        raise HTTPException(500, detail=f"Invalid characters in File name - {file_name}")

    # File name max length validation
    if len(file_name) > 255:
        raise HTTPException(500, detail="File name value exceeds maximum length of 255 characters")

    # File extension validation
    if rule_file.content_type != "application/octet-stream" or not rule_file.filename.lower().endswith(
            ALLOWED_EXTENSION):
        raise HTTPException(500, detail="Invalid document type, only TOML file is supported")

    # File size validation
    max_size: int = 1000000
    content = rule_file.file.read()
    file_size = len(content)
    if file_size > max_size:
        raise HTTPException(500, detail="File size exceeds the maximum limit 1 MB")

    toml_content = str(content, 'utf-8')
    return toml_content
