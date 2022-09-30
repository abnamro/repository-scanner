import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const BranchService = {
  async getFindingsCountByStatusForBranch(branchInfoId) {
    return axios.get(`/branches-info/${branchInfoId}/findings-metadata`);
  },
};
export default BranchService;
