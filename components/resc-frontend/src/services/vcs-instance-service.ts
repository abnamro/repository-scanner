import axiosRetry from 'axios-retry';
import axios, { type AxiosResponse } from 'axios';
import type { paths } from './schema';
import { toRaw } from '@/utils/common-utils';

axiosRetry(axios, { retries: 3 });

const VCSInstanceService = {
  getVCSInstance(
    vcsInstanceId: number
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/vcs-instances/{vcs_instance_id}']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/vcs-instances/${toRaw(vcsInstanceId)}`);
  },
};

export default VCSInstanceService;
