import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const FindingsService = {
  async getFindingById(findingId) {
    return axios.get(`/findings/${findingId}`);
  },

  async auditFindings(findingIds, findingStatus, comment) {
    const commentVal = comment == null ? '' : comment;

    return axios.post(`/findings/audit/`, {
      finding_ids: findingIds,
      status: findingStatus,
      comment: commentVal,
    });
  },

  async getDetailedFindings(filter) {
    let query_string = '';

    if (filter.scanIds) {
      query_string += `&scan_ids=${encodeURIComponent(JSON.stringify(filter.scanIds))}`;
    }

    if (filter.rule) {
      query_string += `&rule_names=${encodeURIComponent(JSON.stringify(filter.rule))}`;
    }
    if (filter.findingStatus) {
      query_string += `&finding_statuses=${encodeURIComponent(
        JSON.stringify(filter.findingStatus)
      )}`;
    }
    if (filter.vcsProvider) {
      query_string += `&vcs_providers=${encodeURIComponent(JSON.stringify(filter.vcsProvider))}`;
    }
    if (filter.project) {
      query_string += `&project_name=${filter.project}`;
    }
    if (filter.repository) {
      query_string += `&repository_name=${filter.repository}`;
    }
    if (filter.branch) {
      query_string += `&branch_name=${filter.branch}`;
    }
    if (filter.startDate) {
      query_string += `&start_date_time=${filter.startDate}T00:00:00`;
    }
    if (filter.endDate) {
      query_string += `&end_date_time=${filter.endDate}T23:59:59`;
    }
    if (filter.rulePackVersions) {
      query_string += `&rule_pack_versions=${encodeURIComponent(
        JSON.stringify(filter.rulePackVersions)
      )}`;
    }
    if (filter.ruleTags) {
      query_string += `&rule_tags=${encodeURIComponent(JSON.stringify(filter.ruleTags))}`;
    }
    if (query_string) {
      query_string = query_string.substring(1);
    } else {
      query_string = null;
    }

    return axios.get(`/detailed-findings`, {
      params: {
        skip: filter.skip,
        limit: filter.limit,
        query_string: query_string,
      },
    });
  },

  async getFindingCountPerWeek() {
    return axios.get(`/findings/count-by-time/week`);
  },

  async getMetricsFindingsCountPerVcsProviderPerWeek() {
    return axios.get(`/metrics/count-per-vcs-provider-by-week`);
  },
  async getUnTriagedCountPerVcsProviderPerWeek() {
    return axios.get(`/metrics/un-triaged-count-over-time`);
  },
  async getTruePositiveCountPerVcsProviderPerWeek() {
    return axios.get(`/metrics/audited-count-over-time`);
  },
  async getAuditsByAuditorPerWeek() {
    return axios.get(`/metrics/audit-count-by-auditor-over-time`);
  },

  async getFindingAudits(findingId, perPage, skipRowCount) {
    return axios.get(`findings/${findingId}/audit`, {
      params: {
        skip: skipRowCount,
        limit: perPage,
      },
    });
  },
};

export default FindingsService;
