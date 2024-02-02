import axiosRetry from 'axios-retry';
import axios, { type AxiosResponse } from 'axios';
import type { paths } from './schema';
import QueryUtils from '@/utils/query-utils';

axiosRetry(axios, { retries: 3 });

const RepositoryService = {
  async getRepositoriesWithFindingsMetadata(
    perPage: number,
    skipRowCount: number,
    vcsTypeList: string[],
    projectFilter: string | undefined,
    repositoryFilter: string | undefined,
    includeZeroFindingRepos = true
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/repositories/findings-metadata/']['get']['responses']['200']['content']['application/json']
    >
  > {
    let queryParams = '';
    queryParams += QueryUtils.appendExplodArrayIf('vcsprovider', vcsTypeList);
    queryParams += QueryUtils.appendIf('skip', skipRowCount);
    queryParams += QueryUtils.appendIf('limit', perPage);
    queryParams += QueryUtils.appendIf('projectfilter', projectFilter);
    queryParams += QueryUtils.appendIf('repositoryfilter', repositoryFilter);
    queryParams += QueryUtils.appendBool('onlyifhasfindings', includeZeroFindingRepos === false);
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/repositories/findings-metadata/?${queryParams}`);
  },

  async getLastScanForRepository(
    repositoryId: string
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/repositories/{repository_id}/last-scan']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/repositories/${repositoryId}/last-scan`);
  },

  async getVCSProviders(): Promise<
    AxiosResponse<
      paths['/resc/v1/supported-vcs-providers']['get']['responses']['200']['content']['application/json']
    >
  > {
    return axios.get(`/supported-vcs-providers`);
  },

  async getDistinctProjects(
    vcsTypeList: string[],
    repositoryFilter: string | undefined,
    includeZeroFindingRepos = true
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/repositories/distinct-projects/']['get']['responses']['200']['content']['application/json']
    >
  > {
    let queryParams = '';
    queryParams += QueryUtils.appendExplodArrayIf('vcsprovider', vcsTypeList);
    queryParams += QueryUtils.appendIf('repositoryfilter', repositoryFilter);
    queryParams += QueryUtils.appendBool('onlyifhasfindings', includeZeroFindingRepos === false);
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/repositories/distinct-projects/?${queryParams}`);
  },

  async getDistinctRepositories(
    vcsTypeList: string[],
    projectFilter: string | undefined,
    includeZeroFindingRepos = true
  ): Promise<
    AxiosResponse<
      paths['/resc/v1/repositories/distinct-repositories/']['get']['responses']['200']['content']['application/json']
    >
  > {
    let queryParams = '';
    queryParams += QueryUtils.appendExplodArrayIf('vcsprovider', vcsTypeList);
    queryParams += QueryUtils.appendIf('projectname', projectFilter);
    queryParams += QueryUtils.appendBool('onlyifhasfindings', includeZeroFindingRepos === false);
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/repositories/distinct-repositories/?${queryParams}`);
  },
};

export default RepositoryService;
