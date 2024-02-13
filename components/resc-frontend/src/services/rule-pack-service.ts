import axiosRetry from 'axios-retry';
import axios, { type AxiosResponse } from 'axios';
import type { paths } from './schema';
import { toRaw } from '@/utils/common-utils';
import QueryUtils from '@/utils/query-utils';

axiosRetry(axios, { retries: 3 });

const RulePackService = {
  async getRulePackVersions(
    perPage: number | undefined = undefined,
    skipRowCount: number | undefined = undefined,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/rule-packs/versions']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`rule-packs/versions`, {
      params: {
        skip: toRaw(skipRowCount),
        limit: toRaw(perPage),
      },
    });
  },

  async uploadRulePack(
    version: string,
    ruleFile: File,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/rule-packs']['post']['responses']['200']['content']['application/json']
    >
  > {
    const formData = new FormData();
    formData.append('rule_file', ruleFile);
    return axios.post(`/rule-packs?version=${version}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  async downloadRulePack(
    rulePackVersion: string,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/rule-packs']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/rule-packs`, {
      params: {
        rule_pack_version: toRaw(rulePackVersion),
      },
      responseType: 'arraybuffer',
    });
  },

  async getRuleTagsByRulePackVersions(
    rulePackVersions: string[],
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/rule-packs/tags']['get']['responses']['200']['content']['application/json']
    >
  > {
    let queryParams = '';
    queryParams += QueryUtils.appendExplodArrayIf('version', rulePackVersions);
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/rule-packs/tags?${queryParams}`);
  },
};

export default RulePackService;
