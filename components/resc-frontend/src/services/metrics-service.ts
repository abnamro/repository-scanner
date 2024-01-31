import axiosRetry from 'axios-retry';
import axios, { type AxiosResponse } from 'axios';
import type { paths } from './schema';

axiosRetry(axios, { retries: 3 });

const MetricsService = {
  async getPersonalAuditMetrics(): Promise<
    AxiosResponse<
      paths['/resc/v1/metrics/personal-audits']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`metrics/personal-audits`);
  },
};

export default MetricsService;
