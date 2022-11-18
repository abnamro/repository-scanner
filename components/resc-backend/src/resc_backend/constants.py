PROJECT_QUEUE = "projects"
REPOSITORY_QUEUE = "repositories"

BITBUCKET = "BITBUCKET"
AZURE_DEVOPS = "AZURE_DEVOPS"
GITHUB_PUBLIC = "GITHUB_PUBLIC"

# RWS: RESC Web Service
RWS_VERSION_PREFIX = "/resc/v1"
RWS_ROUTE_REPOSITORIES = "/repositories"
RWS_ROUTE_BRANCHES = "/branches"
RWS_ROUTE_SCANS = "/scans"
RWS_ROUTE_LAST_SCAN = "/last-scan"
RWS_ROUTE_FINDINGS = "/findings"
RWS_ROUTE_RULES = "/rules"
RWS_ROUTE_DETAILED_FINDINGS = "/detailed-findings"
RWS_ROUTE_TOTAL_COUNT_BY_RULE = "/total-count-by-rule"
RWS_ROUTE_BY_RULE = "/by-rule"
RWS_ROUTE_DETECTED_RULES = "/detected-rules"
RWS_ROUTE_FINDINGS_METADATA = "/findings-metadata"
RWS_ROUTE_FINDING_STATUS_COUNT = "/finding-status-count"
RWS_ROUTE_UPLOAD_RULE_PACK = "/upload-rule-pack"
RWS_ROUTE_DOWNLOAD_RULE_PACK = "/download-rule-pack"
RWS_ROUTE_RULE_ALLOW_LIST = "/rule-allow-list"
RWS_ROUTE_RULE_PACK = "/rule-pack"
RWS_ROUTE_RULE_PACKS = "/rule-packs"
RWS_ROUTE_VCS = "/vcs-instances"

RWS_ROUTE_COUNT_BY_TIME = "/count-by-time"
RWS_ROUTE_SUPPORTED_VCS_PROVIDERS = "/supported-vcs-providers"
RWS_ROUTE_SUPPORTED_STATUSES = "/supported-statuses"
RWS_ROUTE_DISTINCT_PROJECTS = "/distinct-projects"
RWS_ROUTE_DISTINCT_REPOSITORIES = "/distinct-repositories"
COMMON_TAG = "resc-common"

RWS_ROUTE_AUDIT = "/audit"

RWS_ROUTE_AUTH_CHECK = "/auth-check"

RWS_ROUTE_HEALTH = "/health"

REPOSITORIES_TAG = "resc-repositories"
BRANCHES_TAG = "resc-branches"
SCANS_TAG = "resc-scans"
FINDINGS_TAG = "resc-findings"
RULES_TAG = "resc-rules"
HEALTH_TAG = "health"
VCS_TAG = "resc-vcs-instances"

DEFAULT_RECORDS_PER_PAGE_LIMIT = 100
MAX_RECORDS_PER_PAGE_LIMIT = 500

RESC_OPERATOR_ROLE = "SG_APP_RESC_OPERATOR"

BASE_SCAN = "BASE"
INCREMENTAL_SCAN = "INCREMENTAL"

CACHE_MAX_AGE = "max-age=604800"

TOML_CUSTOM_DELIMITER = "#custom-delimiter#"
TEMP_RULE_FILE = "/tmp/temp_resc_rule.toml"
ALLOWED_EXTENSION = ".toml"

# Logging
LOG_FILE_PATH_RABBITMQ = "rabbitmq_initialization.log"
LOGGING_FILE = "logging.ini"
