import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const VCSInstanceService = {
  getVCSInstance(vcsInstanceId) {
    return axios.get(`/vcs-instances/${vcsInstanceId}`);
  },
};

export default VCSInstanceService;
