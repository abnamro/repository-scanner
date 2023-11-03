# pylint: disable=E1101
# Standard Library
import csv
import logging
from datetime import datetime

# Third Party
import dateutil.parser

logger = logging.getLogger(__name__)


class IgnoredListProvider():  # pylint: disable=R0902

    def __init__(self, ignore_findings_path: str):
        self.ignore_findings_path: str = ignore_findings_path
        self.today: datetime = datetime.now()

    def get_ignore_list(self) -> dict:
        """
            Get the dictionary of ignored findings according to the file
            The output will contain a dictionary with the findings id as the key and the tags as a list in the value
        """
        ignored = {}

        if self.ignore_findings_path is None:
            return ignored

        try:
            # read dsv: `path|rule_name|line_number|expiry_date`
            with open(self.ignore_findings_path, encoding="utf-8") as ignore_findings_file:
                csv_ignore_list = csv.reader(ignore_findings_file, delimiter='|')
                for row in csv_ignore_list:
                    expire: datetime = datetime.now()

                    # rows starting with # are comments
                    if row[0][:1] == '#':
                        continue

                    if len(row) < 3:
                        string_row: str = "".join(row)
                        logger.warning(f"Skipping: incomplete entry for {string_row}")
                        continue

                    path = row[0]
                    rule = row[1]
                    line = row[2]
                    if len(row) > 3:
                        date = row[3]
                        try:
                            expire: datetime = dateutil.parser.isoparse(date)
                        except ValueError:
                            logger.warning(f"Skipping: invalid date entry for {path}: {date}")
                            continue

                    if expire < self.today:
                        logger.warning(f"Info: expired date entry for {date}")
                        continue

                    # we use the path, rule_name, line_number as a dictionary key
                    ignored[f"{path}|{rule}|{line}"] = True
        except FileNotFoundError:  # <- File does not exists: we just fail silently
            logger.warning(f"could not find {self.ignore_findings_path}")
            return {}

        return ignored
