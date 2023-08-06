# Standard Library
import logging
import random
import sys
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from datetime import datetime, timedelta

# Third Party
from cliparser import CliParser
from db_util import DbUtil

# First Party
from resc_backend.common import initialise_logs
from resc_backend.constants import AZURE_DEVOPS, BITBUCKET, GITHUB_PUBLIC, LOG_FILE_DUMMY_DATA_GENERATOR
from resc_backend.db.model import (
    DBaudit,
    DBfinding,
    DBrepository,
    DBrule,
    DBruleAllowList,
    DBrulePack,
    DBruleTag,
    DBscan,
    DBscanFinding,
    DBtag,
    DBVcsInstance
)
from resc_backend.resc_web_service.schema.finding_status import FindingStatus
from resc_backend.resc_web_service.schema.scan_type import ScanType

logger_config = initialise_logs(LOG_FILE_DUMMY_DATA_GENERATOR)
logger = logging.getLogger(__name__)


class GenerateData:
    """Generates a specified number of records to a target table in the db."""

    def __init__(self):
        self.finding_id_chunks = None
        self.rule_allow_list_ids = None
        self.rule_pack_versions = []
        self.finding_ids = None
        self.repo_ids = None

        self.db_util = DbUtil()
        self.seco_members = ["Ingmar", "Peter", "Amrit", "Damien", "Usman", "Fatma", "Ajai", "Anonymous"]

        self.tags = ["Cli", "Warn", "Sentinel"]
        self.scan_types = [ScanType.BASE, ScanType.INCREMENTAL]
        self.vcs_instance_types = [BITBUCKET, AZURE_DEVOPS, GITHUB_PUBLIC]
        self.audit_status = [FindingStatus.NOT_ANALYZED, FindingStatus.CLARIFICATION_REQUIRED,
                             FindingStatus.FALSE_POSITIVE, FindingStatus.TRUE_POSITIVE]

    @staticmethod
    def get_random_audit_datetime():
        start = datetime.now() - timedelta(weeks=2)
        return GenerateData.get_random_datetime(start)

    @staticmethod
    def get_random_scan_datetime():
        start = datetime.now() - timedelta(weeks=6)
        return GenerateData.get_random_datetime(start)

    @staticmethod
    def get_random_commit_datetime():
        start = datetime.now() - timedelta(weeks=12)
        return GenerateData.get_random_datetime(start)

    @staticmethod
    def get_random_datetime(start: datetime):
        end = datetime.now()
        random_date = start + (end - start) * random.random()
        return random_date

    @staticmethod
    def determine_chunk_size(size: int):
        if size >= 10000:
            return 10000
        if size >= 1000 <= 10000:
            return 1000
        if 200 <= size <= 1000:
            return 200
        if 100 <= size <= 200:
            return 100
        if size <= 100:
            return 50

    @staticmethod
    def create_chunks(size: int, chunk_size: int):
        """Creates a list of lists based on an arbitrary length."""
        entirety = [i for i in range(1, size + 1)]
        chunked_lists = [entirety[i:i + chunk_size] for i in range(0, size, chunk_size)]
        return chunked_lists

    @staticmethod
    def create_chunks_from_list(list_to_be_chunked: [], chunk_size: int):
        """Creates a list of lists of arbitrary length from a list."""
        chunked_lists = [list_to_be_chunked[i:i + chunk_size] for i in
                         range(0, len(list_to_be_chunked), chunk_size)]
        return chunked_lists

    def init_db(self):
        """Initializes the database for storing the generated data"""
        if not self.db_util.is_db_connected():
            logger.error("Failed in establishing a db connection.")
            sys.exit(-1)
        proceed_prompt = input("All the existing data from the database tables will be dropped.Proceed ? [y/n]")
        logger.info(f"Received [{proceed_prompt}] as response.")
        if proceed_prompt not in ("y", "Y", "yes", "Yes", "YES"):
            logger.info("Won't proceed. Exiting program.")
            exit(0)
        self.db_util.clear_db_tables()

    def init_data_generation(self, property_values: {}):
        self.init_db()
        start = datetime.now()
        self.generate_rule_allow_list()
        self.generate_rule_pack(property_values["active_rule_pack"], property_values["additional"])
        self.generate_rules(int(property_values["rules"]))
        self.generate_tags()
        self.generate_rule_tags()
        self.generate_vcs_instances(property_values["vcs_instances"])
        self.generate_repositories(property_values["repos"])
        self.generate_scans(property_values["scans"])
        self.generate_findings(property_values["findings"])
        self.generate_scan_findings(),
        self.generate_audits()
        logger.info("Duration [{}]".format(datetime.now() - start))
        # shutdown properly
        self.db_util.shut_down()

    def generate_rule_allow_list(self):
        rule_allow_list = [DBruleAllowList(description="test rule allow list", regexes="*.*")]
        self.db_util.persist_data(rule_allow_list)
        # caching rule_allow_list ids for future use
        self.rule_allow_list_ids = self.db_util.get_data_for_single_attr(DBruleAllowList, "id_")
        logger.info(f"Generated [{DBruleAllowList.__tablename__}]")

    def generate_rule_pack(self, active: str, additional: str):
        allow_list_id = self.rule_allow_list_ids[0]
        rule_pack = [dict(version=active,
                          global_allow_list=allow_list_id,
                          active=1)]
        self.rule_pack_versions.append(active)
        if additional:
            versions = additional.split(",")
            for version in versions:
                rule_pack.append(dict(version=version.strip(),
                                      global_allow_list=allow_list_id,
                                      active=0))
                self.rule_pack_versions.append(version)
        self.db_util.bulk_persist_data(DBrulePack, rule_pack)
        logger.info(f"Generated [{DBrulePack.__tablename__}]")

    def generate_rules(self, amount_to_generate: int):
        # random.choice to arbitrarily match in case more rule_pack_versions and rule_allow_lists would be introduced
        rules = [dict(rule_pack=random.choice(self.rule_pack_versions),
                      allow_list=self.rule_allow_list_ids[0],
                      rule_name=f"rule#{num}",
                      description=f"rule number {num}",
                      regex="*.*") for num in range(1, amount_to_generate + 1)]
        self.db_util.bulk_persist_data(DBrule, rules)
        logger.info(f"Generated [{DBrule.__tablename__}]")

    def generate_tags(self):
        tags = [dict(name=tag) for tag in self.tags]
        self.db_util.bulk_persist_data(DBtag, tags)
        logger.info(f"Generated [{DBtag.__tablename__}]")

    def generate_rule_tags(self):
        rule_ids = self.db_util.get_data_for_single_attr(DBrule, "id_")
        tag_ids = self.db_util.get_data_for_single_attr(DBtag, "id_")
        rule_tags = [dict(rule_id=rule_id, tag_id=random.choice(tag_ids)) for rule_id in rule_ids]
        self.db_util.bulk_persist_data(DBruleTag, rule_tags)
        logger.info(f"Generated [{DBruleTag.__tablename__}]")

    def generate_vcs_instances(self, amount_to_generate: int):
        vcs_instances = []
        for num in range(1, int(amount_to_generate) + 1):
            vcs_type = random.choice(self.vcs_instance_types)
            name = f"{vcs_type.lower()}-server-{num}"
            vcs_instances.append(dict(name=name,
                                      provider_type=vcs_type,
                                      scheme="https",
                                      hostname=f"hostname{num}",
                                      port=123,
                                      organization="my-org",
                                      scope=None,
                                      exceptions=None))
        self.db_util.bulk_persist_data(DBVcsInstance, vcs_instances)
        logger.info(f"Generated [{DBVcsInstance.__tablename__}]")

    def generate_repositories(self, amount_to_generate: int):
        vcs_instance_ids = self.db_util.get_data_for_single_attr(DBVcsInstance, "id_")
        chunk_size = GenerateData.determine_chunk_size(amount_to_generate)
        chunks = GenerateData.create_chunks(amount_to_generate, chunk_size)
        for chunk in chunks:
            repos = [dict(vcs_instance=random.choice(vcs_instance_ids),
                          project_key=f"project-key-{num}",
                          repository_id=f"repo-id-{num}",
                          repository_url=f"https://fake-host.com/p1/r/{num}",
                          repository_name=f"repo-name-{num}") for num in range(chunk[0], chunk[-1] + 1)]
            self.db_util.bulk_persist_data(DBrepository, repos)
        # caching repo ids for future use
        self.repo_ids = self.db_util.get_data_for_single_attr(DBrepository, "id_")
        logger.info(f"Generated [{DBrepository.__tablename__}]")

    def generate_scans(self, amount_to_generate: int):
        # Ensure that every repo gets a BASE scan with each of the rule_pack.
        total_scans = []
        for repo_id in self.repo_ids:
            scans_allocated_per_repo = []
            for rule_pack_version in self.rule_pack_versions:
                scans_allocated_per_repo.append(dict(rule_pack=rule_pack_version,
                                                     repository_id=repo_id,
                                                     scan_type=ScanType.BASE,
                                                     last_scanned_commit=f"commit_{random.randint(1, 100)}",
                                                     timestamp=GenerateData.get_random_scan_datetime(),
                                                     increment_number=0))
            # now that every repo has a BASE scan, incremental scans can also be generated for the same rule-pack.
            remaining_scans_per_repo = amount_to_generate - len(scans_allocated_per_repo)
            for _ in range(0, remaining_scans_per_repo):
                scan_type=random.choice(self.scan_types)
                scans_allocated_per_repo.append(dict(rule_pack=random.choice(self.rule_pack_versions),
                                                     repository_id=repo_id,
                                                     scan_type=scan_type,
                                                     last_scanned_commit=f"commit_{random.randint(1, 100)}",
                                                     timestamp=GenerateData.get_random_scan_datetime(),
                                                     increment_number=1 if scan_type == ScanType.INCREMENTAL else 0))
            total_scans.extend(scans_allocated_per_repo)
        self.db_util.bulk_persist_data(DBscan, scans)
        logger.info(f"Generated [{DBscan.__tablename__}]")

    def generate_findings(self, amount_to_generate: int):
        chunk_size = GenerateData.determine_chunk_size(amount_to_generate)
        chunks = GenerateData.create_chunks(amount_to_generate, chunk_size)
        rule_names = self.db_util.get_data_for_single_attr(DBrule, "rule_name")
        for chunk in chunks:
            findings = []
            for num in range(chunk[0], chunk[-1] + 1):
                column_start = random.randint(1, 500)
                findings.append(dict(repository_id=random.choice(self.repo_ids),
                                     rule_name=random.choice(rule_names),
                                     file_path=f"/path/to/file/{num}",
                                     line_number=random.randint(1, 1000),
                                     column_start=column_start,
                                     column_end=random.randint(column_start + 1, column_start + 25),
                                     commit_id=f"commit_{num}",
                                     commit_message=f"commit_text_{num}",
                                     commit_timestamp=GenerateData.get_random_commit_datetime(),
                                     author=f"some_name_{num}",
                                     email=f"some_mail_{num}",
                                     event_sent_on=None))
            self.db_util.bulk_persist_data(DBfinding, findings)
        # caching finding ids for further use
        self.finding_ids = self.db_util.get_data_for_multiple_attr(DBfinding, ["id_", "repository_id"])
        logger.info(f"Generated [{DBfinding.__tablename__}]")

    def generate_scan_findings(self):
        scan_repo_ids = self.db_util.get_data_for_multiple_attr(DBscan, ["id_", "repository_id"])
        # required because the repository associated with a finding needs to match the repository of the scan
        # group scan_ids by repository
        repo_scan_ids = defaultdict(list)
        for scan_id, repo_id in scan_repo_ids:
            repo_scan_ids[repo_id].append(scan_id)

        chunk_size = GenerateData.determine_chunk_size(len(self.finding_ids))
        # cache for audits
        self.finding_id_chunks = GenerateData.create_chunks_from_list(self.finding_ids, chunk_size)
        for chunk in self.finding_id_chunks:
            scan_findings = []
            for finding_id, repository_id in chunk:
                scan_ids = repo_scan_ids.get(repository_id)
                if scan_ids:
                    scan_findings.append(dict(finding_id=finding_id,
                                              scan_id=random.choice(scan_ids)))
                else:
                    logger.info(f"No scans associated with repository_id [{repository_id}]")
            self.db_util.bulk_persist_data(DBscanFinding, scan_findings)
        logger.info(f"Generated [{DBscanFinding.__tablename__}]")

    def generate_audits(self):
        for chunk in self.finding_id_chunks:
            audits = []
            for finding_id in chunk:
                audits.append(dict(finding_id=finding_id[0],
                                   status=random.choice(self.audit_status),
                                   auditor=random.choice(self.seco_members),
                                   comment="just trust me",
                                   timestamp=GenerateData.get_random_audit_datetime()))
            self.db_util.bulk_persist_data(DBaudit, audits)
        logger.info(f"Generated [{DBaudit.__tablename__}]")


if __name__ == "__main__":
    values = {}
    parser: ArgumentParser = CliParser().create_cli_argparser()
    args: Namespace = parser.parse_args()

    values["active_rule_pack"] = args.active_rulepack
    values["additional"] = args.additional_rulepacks
    values["rules"] = args.rules_generate_amount
    values["vcs_instances"] = args.vcs_instances_generate_amount
    values["repos"] = args.repos_generate_amount
    values["scans"] = args.max_scans_per_repo_generate_amount
    values["findings"] = args.findings_generate_amount

    if values["additional"] and int(values["scans"] < 1 + len(values["additional"].split(","))):
        print("Max scans per repo should be greater than or equal to total number of rule-packs.")
        sys.exit(-1)

    total_scans_to_generate = int(values["repos"]) * int(values["scans"])
    values["scans"] = total_scans_to_generate

    generate_data = GenerateData()
    generate_data.init_data_generation(values)
