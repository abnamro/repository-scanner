PROJECT_QUEUE = "projects"
REPOSITORY_QUEUE = "repositories"

BITBUCKET = "BITBUCKET"
AZURE_DEVOPS = "AZURE_DEVOPS"
GITHUB_PUBLIC = "GITHUB_PUBLIC"

# RWS: RESC Web Service
RWS_VERSION_PREFIX = "/resc/v1"
RWS_ROUTE_REPOSITORIES = "/repositories"
RWS_ROUTE_SCANS = "/scans"
RWS_ROUTE_LAST_SCAN = "/last-scan"
RWS_ROUTE_FINDINGS = "/findings"
RWS_ROUTE_RULES = "/rules"
RWS_ROUTE_METRICS = "/metrics"
RWS_ROUTE_DETAILED_FINDINGS = "/detailed-findings"
RWS_ROUTE_TOTAL_COUNT_BY_RULE = "/total-count-by-rule"
RWS_ROUTE_BY_RULE = "/by-rule"
RWS_ROUTE_DETECTED_RULES = "/detected-rules"
RWS_ROUTE_FINDINGS_METADATA = "/findings-metadata"
RWS_ROUTE_FINDING_STATUS_COUNT = "/finding-status-count"
RWS_ROUTE_RULE_PACKS = "/rule-packs"
RWS_ROUTE_VCS = "/vcs-instances"


RWS_ROUTE_PERSONAL_AUDITS = "/personal-audits"
RWS_ROUTE_AUDIT_COUNT_BY_AUDITOR_OVER_TIME = "/audit-count-by-auditor-over-time"
RWS_ROUTE_AUDITED_COUNT_OVER_TIME = "/audited-count-over-time"
RWS_ROUTE_UN_TRIAGED_COUNT_OVER_TIME = "/un-triaged-count-over-time"
RWS_ROUTE_COUNT_BY_TIME = "/count-by-time"
RWS_ROUTE_COUNT_PER_VCS_PROVIDER_BY_WEEK = "/count-per-vcs-provider-by-week"
RWS_ROUTE_SUPPORTED_VCS_PROVIDERS = "/supported-vcs-providers"
RWS_ROUTE_SUPPORTED_STATUSES = "/supported-statuses"
RWS_ROUTE_DISTINCT_PROJECTS = "/distinct-projects"
RWS_ROUTE_DISTINCT_REPOSITORIES = "/distinct-repositories"
COMMON_TAG = "resc-common"

RWS_ROUTE_AUDIT = "/audit"

RWS_ROUTE_AUTH_CHECK = "/auth-check"

RWS_ROUTE_HEALTH = "/health"

REPOSITORIES_TAG = "resc-repositories"
SCANS_TAG = "resc-scans"
FINDINGS_TAG = "resc-findings"
RULES_TAG = "resc-rules"
RULE_PACKS_TAG = "resc-rule-packs"
HEALTH_TAG = "health"
VCS_TAG = "resc-vcs-instances"
METRICS_TAG = "resc-metrics"

DEFAULT_RECORDS_PER_PAGE_LIMIT = 100
MAX_RECORDS_PER_PAGE_LIMIT = 500

BASE_SCAN = "BASE"
INCREMENTAL_SCAN = "INCREMENTAL"

# Cache
CACHE_PREFIX = "resc-cache"
CACHE_NAMESPACE_FINDING = "namespace-finding"
CACHE_NAMESPACE_REPOSITORY = "namespace-repository"
CACHE_NAMESPACE_VCS_INSTANCE = "namespace-vcs-instance"
CACHE_NAMESPACE_RULE_PACK = "namespace-rule-pack"
CACHE_NAMESPACE_RULE = "namespace-rule"
CACHE_NAMESPACE_FINDING_STATUS = "namespace-finding-status"

TOML_CUSTOM_DELIMITER = "#custom-delimiter#"
TEMP_RULE_FILE = "/tmp/temp_resc_rule.toml"
ALLOWED_EXTENSION = ".toml"

# Logging for dummy-data-generator
LOG_FILE_DUMMY_DATA_GENERATOR = "dummy-data-gen.log"

# Logging
LOG_FILE_PATH_RABBITMQ = "rabbitmq_initialization.log"
LOG_FILE_CACHING = "redis_cache.log"
LOGGING_FILE = "logging.ini"

# Error message
ERROR_MESSAGE_500 = "Internal server error. Contact your system administrator"
ERROR_MESSAGE_503 = "Unable to communicate with DataBase, Please contact your system administrator"

# Redis Cache
REDIS_CACHE_EXPIRE = 60*60*24  # set to 24 hours

# HTTP Security Response Headers
STRICT_TRANSPORT_SECURITY = "max-age=31536000; includeSubDomains; preload"
CACHE_CONTROL = "no-cache, no-store"
CROSS_ORIGIN_RESOURCE_POLICY = "same-site"
REFERRER_POLICY = "same-origin"
X_PERMITTED_CROSS_DOMAIN_POLICIES = "none"
X_CONTENT_TYPE_OPTIONS = "nosniff"
X_FRAME_OPTIONS = "DENY"
X_XSS_PROTECTION = "1; mode=block"
CONTENT_SECURITY_POLICY = "default-src 'none'; script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; " \
                          "connect-src 'self'; img-src 'self' https://fastapi.tiangolo.com data:;style-src " \
                          "'self' https://fonts.googleapis.com https://cdn.jsdelivr.net 'unsafe-inline';" \
                          "frame-ancestors 'self'; form-action 'self';"
