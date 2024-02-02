import axiosRetry from 'axios-retry';
import axios, { type AxiosResponse } from 'axios';
import type { paths } from './schema';
import type { FindingStatus, VCSProviders } from './shema-to-types';
import { toRaw } from '@/utils/common-utils';
import QueryUtils from '@/utils/query-utils';

axiosRetry(axios, { retries: 3 });

export type QueryFilterType = {
  scanIds?: number[];
  rule?: string[];
  findingStatus?: FindingStatus[];
  vcsProvider?: VCSProviders[];
  project?: string | undefined;
  repository?: string | undefined;
  startDate?: string | undefined;
  endDate?: string | undefined;
  rulePackVersions?: string[];
  ruleTags?: string[];
  skip: number;
  limit: number;
};

const FindingsService = {
  async getFindingById(
    findingId: string
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/findings/{finding_id}']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/findings/${findingId}`);
  },

  async auditFindings(
    findingIds: number[],
    findingStatus: FindingStatus,
    comment: string
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/findings/audit/']['post']['responses']['201']['content']['application/json']
    >
  > {
    const commentVal = comment == null ? '' : comment;

    return axios.post(`/findings/audit/`, {
      finding_ids: toRaw(findingIds),
      status: toRaw(findingStatus),
      comment: toRaw(commentVal),
    });
  },

  async getDetailedFindings(
    filter: QueryFilterType
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/detailed-findings']['get']['responses']['200']['content']['application/json']
    >
  > {
    let queryString: string | null = '';
    queryString += QueryUtils.appendArrayIf('scan_ids', filter.scanIds);
    queryString += QueryUtils.appendArrayIf('rule_names', filter.rule);
    queryString += QueryUtils.appendArrayIf('finding_statuses', filter.findingStatus);
    queryString += QueryUtils.appendArrayIf('vcs_providers', filter.vcsProvider);
    queryString += QueryUtils.appendIf('project_name', filter.project);
    queryString += QueryUtils.appendIf('repository_name', filter.repository);
    queryString += QueryUtils.appendIf('start_date_time', filter.startDate, 'T00:00:00');
    queryString += QueryUtils.appendIf('end_date_time', filter.endDate, 'T23:59:59');
    queryString += QueryUtils.appendArrayIf('rule_pack_versions', filter.rulePackVersions);
    queryString += QueryUtils.appendArrayIf('rule_tags', filter.ruleTags);
    if (queryString !== '') {
      queryString = queryString.substring(1);
    } else {
      queryString = null;
    }

    return axios.get(`/detailed-findings`, {
      params: {
        skip: filter.skip,
        limit: filter.limit,
        query_string: queryString,
      },
    });
  },

  async getFindingCountPerWeek(): Promise<
    AxiosResponse<
      paths['/resc/v1/findings/count-by-time/{time_type}']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/findings/count-by-time/week`);
  },

  async getMetricsFindingsCountPerVcsProviderPerWeek(): Promise<
    AxiosResponse<
      paths['/resc/v1/metrics/count-per-vcs-provider-by-week']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/metrics/count-per-vcs-provider-by-week`);
  },

  async getUnTriagedCountPerVcsProviderPerWeek(): Promise<
    AxiosResponse<
      paths['/resc/v1/metrics/un-triaged-count-over-time']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/metrics/un-triaged-count-over-time`);
  },

  async getTruePositiveCountPerVcsProviderPerWeek(): Promise<
    AxiosResponse<
      paths['/resc/v1/metrics/audited-count-over-time']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/metrics/audited-count-over-time`);
  },

  async getAuditsByAuditorPerWeek(): Promise<
    AxiosResponse<
      paths['/resc/v1/metrics/audit-count-by-auditor-over-time']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/metrics/audit-count-by-auditor-over-time`);
  },

  async getFindingAudits(
    findingId: number,
    perPage: number,
    skipRowCount: number
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/findings/{finding_id}/audit']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`findings/${findingId}/audit`, {
      params: {
        skip: toRaw(skipRowCount),
        limit: toRaw(perPage),
      },
    });
  },
};

export default FindingsService;
