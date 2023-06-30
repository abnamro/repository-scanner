import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const ScanFindingsService = {
  async getRepositoryById(repositoryId) {
    return axios.get(`/repositories/${repositoryId}`);
  },
  async getScanById(scanId) {
    return axios.get(`/scans/${scanId}`);
  },

  async getRulesByScanIds(scanIds) {
    let queryParams = '';
    if (scanIds) {
      scanIds.forEach((scanId) => {
        queryParams += `&scan_id=${scanId}`;
      });
    }
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/scans/detected-rules/?${queryParams}`);
  },

  async getScansByRepositoryId(repositoryId, skipRowCount, perPage) {
    return axios.get(`/repositories/${repositoryId}/scans`, {
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
