import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const RuleService = {
  async getAllDetectedRules(
    findingStatusList,
    vcsTypeList,
    projectFilter,
    repositoryFilter,
    startDate,
    endDate
  ) {
    let queryParams = '';
    if (findingStatusList) {
      findingStatusList.forEach((status) => {
        queryParams += `&findingstatus=${status}`;
      });
    }
    if (vcsTypeList) {
      vcsTypeList.forEach((name) => {
        queryParams += `&vcsprovider=${name}`;
      });
    }
    if (projectFilter) {
      queryParams += `&projectname=${projectFilter}`;
    }
    if (repositoryFilter) {
      queryParams += `&repositoryname=${repositoryFilter}`;
    }
    if (startDate) {
      queryParams += `&start_date_time=${startDate}T00:00:00`;
    }
    if (endDate) {
      queryParams += `&end_date_time=${endDate}T23:59:59`;
    }
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }
    return axios.get(`/detected-rules?${queryParams}`);
  },

  async getRulesWithFindingStatusCount() {
    return axios.get(`/rules/finding-status-count`);
  },

  async getRulePacks(perPage, skipRowCount) {
    return axios.get(`/rules/rule-packs`, {
      params: {
        skip: skipRowCount,
        limit: perPage,
      },
    });
  },

  async uploadRulePack(ruleFile) {
    const formData = new FormData();
    formData.append('rule_file', ruleFile);
    return axios.post(`/rules/upload-rule-pack`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  async downloadRulePack(rulePackVersion) {
    return axios.get(`/rules/download-rule-pack`, {
      params: {
        rule_pack_version: rulePackVersion,
      },
      responseType: 'arraybuffer',
    });
  },
};

export default RuleService;
