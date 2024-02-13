import axiosRetry from 'axios-retry';
import axios, { type AxiosResponse } from 'axios';
import type { paths } from './schema';
import QueryUtils from '@/utils/query-utils';
import { toRaw } from '@/utils/common-utils';

axiosRetry(axios, { retries: 3 });

const ScanFindingsService = {
  async getRepositoryById(
    repositoryId: number,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/repositories/{repository_id}']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/repositories/${toRaw(repositoryId)}`);
  },

  async getScanById(
    scanId: number,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/scans/{scan_id}']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/scans/${toRaw(scanId)}`);
  },

  async getRulesByScanIds(
    scanIds: number[],
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/detected-rules']['get']['responses']['200']['content']['application/json']
    >
  > {
    let queryParams = '';
    queryParams += QueryUtils.appendExplodArrayIf('scan_id', scanIds);
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/scans/detected-rules/?${queryParams}`);
  },

  async getScansByRepositoryId(
    repositoryId: number,
    skipRowCount: number,
    perPage: number,
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/repositories/{repository_id}/scans']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/repositories/${toRaw(repositoryId)}/scans`, {
      params: {
        skip: skipRowCount,
        limit: perPage,
      },
    });
  },

  async getStatusList(): Promise<
    AxiosResponse<
      paths['/resc/v1/findings/supported-statuses/']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/findings/supported-statuses/`);
  },
};

export default ScanFindingsService;
