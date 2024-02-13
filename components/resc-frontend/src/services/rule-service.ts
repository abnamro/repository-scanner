import axiosRetry from 'axios-retry';
import axios, { type AxiosResponse } from 'axios';
import type { paths } from './schema';
import QueryUtils from '@/utils/query-utils';
import { toRaw } from '@/utils/common-utils';

axiosRetry(axios, { retries: 3 });

const RuleService = {
  async getAllDetectedRules(
    findingStatusList: string[] | null,
    vcsTypeList: string[] | null,
    projectFilter: string | undefined,
    repositoryFilter: string | undefined,
    startDate: string | undefined,
    endDate: string | undefined,
    rulePackVersions: string[] | null,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/detected-rules']['get']['responses']['200']['content']['application/json']
    >
  > {
    let queryParams = '';
    queryParams += QueryUtils.appendExplodArrayIf('findingstatus', findingStatusList);
    queryParams += QueryUtils.appendExplodArrayIf('vcsprovider', vcsTypeList);
    queryParams += QueryUtils.appendIf('projectname', projectFilter);
    queryParams += QueryUtils.appendIf('repositoryname', repositoryFilter);
    queryParams += QueryUtils.appendIf('start_date_time', startDate, 'T00:00:00');
    queryParams += QueryUtils.appendIf('end_date_time', endDate, 'T23:59:59');
    queryParams += QueryUtils.appendExplodArrayIf('rule_pack_version', rulePackVersions);
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/detected-rules?${queryParams}`);
  },

  async getRulesWithFindingStatusCount(
    rulePackVersions: string[] | null,
    ruleTags: string[] | null,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/rules/finding-status-count']['get']['responses']['200']['content']['application/json']
    >
  > {
    let queryParams = '';
    queryParams += QueryUtils.appendExplodArrayIf('rule_pack_version', rulePackVersions);
    queryParams += QueryUtils.appendExplodArrayIf('rule_tag', ruleTags);
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/rules/finding-status-count?${queryParams}`);
  },

  async getRulePacks(
    perPage: string,
    skipRowCount: string,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/rule-packs']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/rules/rule-packs`, {
      params: {
        skip: toRaw(skipRowCount),
        limit: toRaw(perPage),
      },
    });
  },
};

export default RuleService;
