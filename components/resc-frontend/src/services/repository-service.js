import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });

const RepositoryService = {
  async getRepositoriesWithFindingsMetadata(
    perPage,
    skipRowCount,
    vcsTypeList,
    projectFilter,
    repositoryFilter
  ) {
    let queryParams = '';
    if (vcsTypeList) {
      vcsTypeList.forEach((name) => {
        queryParams += `&vcsprovider=${name}`;
      });
    }
    if (skipRowCount) {
      queryParams += `&skip=${skipRowCount}`;
    }
    if (perPage) {
      queryParams += `&limit=${perPage}`;
    }
    if (projectFilter) {
      queryParams += `&projectfilter=${projectFilter}`;
    }
    if (repositoryFilter) {
      queryParams += `&repositoryfilter=${repositoryFilter}`;
    }

    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/repositories-info/findings-metadata/?${queryParams}`);
  },

  async getRepositoryBranches(repositoryId, perPage, skipRowCount) {
    return axios.get(`/repositories-info/${repositoryId}/branches-info`, {
      params: {
        skip: skipRowCount,
        limit: perPage,
      },
    });
  },

  async getVCSProviders() {
    return axios.get(`/supported-vcs-providers`);
  },

  async getDistinctProjects(vcsTypeList, repositoryFilter) {
    let queryParams = '';
    if (vcsTypeList) {
      vcsTypeList.forEach((name) => {
        queryParams += `&vcsprovider=${name}`;
      });
    }
    if (repositoryFilter) {
      queryParams += `&repositoryfilter=${repositoryFilter}`;
    }
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/repositories-info/distinct-projects/?${queryParams}`);
  },

  async getDistinctRepositories(vcsTypeList, projectFilter) {
    let queryParams = '';
    if (vcsTypeList) {
      vcsTypeList.forEach((name) => {
        queryParams += `&vcsprovider=${name}`;
      });
    }
    if (projectFilter) {
      queryParams += `&projectname=${projectFilter}`;
    }
    if (queryParams) {
      queryParams = queryParams.slice(1);
    }

    return axios.get(`/repositories-info/distinct-repositories/?${queryParams}`);
  },
};

export default RepositoryService;
