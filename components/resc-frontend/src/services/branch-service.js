import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const BranchService = {
  async getFindingsCountByStatusForBranch(branchId) {
    return axios.get(`/branches/${branchId}/findings-metadata`);
  },
};
export default BranchService;
