import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const ScanFindingsService = {
  async getRepositoryInfoById(repositoryInfoId) {
    return axios.get(`/repositories-info/${repositoryInfoId}`);
  },
  async getScanInfoById(scanId) {
    return axios.get(`/scans/${scanId}`);
  },
  async getBranchInfoById(brancheInfoId) {
    return axios.get(`/branches-info/${brancheInfoId}`);
  },

  async getRulesByScanIds(scanIds) {
    let query_string = '';

    if (scanIds) {
      query_string += `&scan_ids=${encodeURIComponent(JSON.stringify(scanIds))}`;
    }
    if (query_string) {
      query_string = query_string.substring(1);
    } else {
      query_string = null;
    }

    return axios.get(`/scans/detected-rules/`, {
      params: {
        query_string: query_string,
      },
    });
  },

  async getScansByBranchId(branchId, perPage, skipRowCount) {
    return axios.get(`/branches-info/${branchId}/scans`, {
      params: {
        skip: skipRowCount,
        limit: perPage,
      },
    });
  },

  async getStatusList() {
    return axios.get(`/findings/supported-statuses/`);
  },

  parseStatusOptions(statusOptions) {
    const statusList = [];
    statusOptions.forEach(function (value, index) {
      const statusJson = {};
      if (value === 'NOT_ANALYZED') {
        statusJson['id'] = index;
        statusJson['label'] = 'Not Analyzed';
        statusJson['value'] = value;
      } else if (value === 'UNDER_REVIEW') {
        statusJson['id'] = index;
        statusJson['label'] = 'Under Review';
        statusJson['value'] = value;
      } else if (value === 'CLARIFICATION_REQUIRED') {
        statusJson['id'] = index;
        statusJson['label'] = 'Clarification Required';
        statusJson['value'] = value;
      } else if (value === 'TRUE_POSITIVE') {
        statusJson['id'] = index;
        statusJson['label'] = 'True Positive';
        statusJson['value'] = value;
      } else if (value === 'FALSE_POSITIVE') {
        statusJson['id'] = index;
        statusJson['label'] = 'False Positive';
        statusJson['value'] = value;
      }
      statusList.push(statusJson);
    });
    return statusList;
  },
};

export default ScanFindingsService;
