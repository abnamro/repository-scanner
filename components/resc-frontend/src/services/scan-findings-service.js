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
};

export default ScanFindingsService;
