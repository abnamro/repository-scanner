import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const MetricsService = {
  async getPersonalAuditMetrics() {
    return axios.get(`metrics/personal-audits`);
  },
};

export default MetricsService;
