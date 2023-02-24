import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const RulePackService = {
  async getRulePackVersions(perPage, skipRowCount) {
    return axios.get(`rule-packs/versions`, {
      params: {
        skip: skipRowCount,
        limit: perPage,
      },
    });
  },

  async uploadRulePack(version, ruleFile) {
    const formData = new FormData();
    formData.append('rule_file', ruleFile);
    return axios.post(`/rule-packs?version=${version}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  async downloadRulePack(rulePackVersion) {
    return axios.get(`/rule-packs`, {
      params: {
        rule_pack_version: rulePackVersion,
      },
      responseType: 'arraybuffer',
    });
  },
};

export default RulePackService;
