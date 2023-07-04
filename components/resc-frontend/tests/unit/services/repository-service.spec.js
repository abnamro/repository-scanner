import RepositoryService from '@/services/repository-service';
import axios from 'axios';
import Config from '@/configuration/config';
import repositories from '@/../tests/resources/mock_repositories.json';

jest.mock('axios');

describe('function getDistinctRepositories', () => {
  let allRepos = ['bb_repo1', 'bb_repo2', 'ado_repo1', 'ado_repo2'];
  let bitbucketRepos = ['bb_repo1', 'bb_repo2'];
  let adoRepos = ['ado_repo1', 'ado_repo2'];
  describe('when API call is successful for getDistinctRepositories', () => {
    it('should return all distinct repositories when no VCS providers provided', async () => {
      axios.get.mockResolvedValueOnce(allRepos);

      const response = await RepositoryService.getDistinctRepositories(null, '');
      expect(response).toEqual(allRepos);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(4);
    });
  });

  describe('when API call is successful for getDistinctRepositories', () => {
    it('should return all distinct repositories when all VCS providers selected', async () => {
      axios.get.mockResolvedValueOnce(allRepos);

      const response = await RepositoryService.getDistinctRepositories(
        [`${Config.value('bitbucketVal')}`, `${Config.value('azureDevOpsVal')}`],
        ''
      );
      expect(response).toEqual(allRepos);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(4);
    });
  });

  describe('when API call is successful', () => {
    it('should return all distinct repositories for typed repository name', async () => {
      axios.get.mockResolvedValueOnce(bitbucketRepos);

      const response = await RepositoryService.getDistinctRepositories(null, 'project-A');

      expect(response).toEqual(bitbucketRepos);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(2);
    });
  });

  describe('when API call is successful', () => {
    it('should return all distinct repositories for bitbucket', async () => {
      axios.get.mockResolvedValueOnce(bitbucketRepos);

      const response = await RepositoryService.getDistinctRepositories(
        [`${Config.value('bitbucketVal')}`],
        null
      );

      expect(response).toEqual(bitbucketRepos);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(2);
    });
  });

  describe('when API call is successful', () => {
    it('should return all distinct repositories for azure devops', async () => {
      axios.get.mockResolvedValueOnce(adoRepos);

      const response = await RepositoryService.getDistinctRepositories(
        [`${Config.value('azureDevOpsVal')}`],
        ''
      );

      expect(response).toEqual(adoRepos);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(2);
    });
  });

  describe('when API call is successful', () => {
    it('should return all distinct bitbucket repositories for selected project', async () => {
      axios.get.mockResolvedValueOnce(bitbucketRepos);

      const response = await RepositoryService.getDistinctRepositories(
        [`${Config.value('bitbucketVal')}`],
        'project-A'
      );

      expect(response).toEqual(bitbucketRepos);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(2);
    });
  });

  describe('when API call is successful', () => {
    it('should return all distinct azure devops repositories for selected project', async () => {
      axios.get.mockResolvedValueOnce(adoRepos);

      const response = await RepositoryService.getDistinctRepositories(
        [`${Config.value('azureDevOpsVal')}`],
        'project-A'
      );

      expect(response).toEqual(adoRepos);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(2);
    });
  });
});

describe('function getRepositoriesWithFindingsMetadata', () => {
  it('fetch a set of repositories with findings metadata, results should be paginated', async () => {
    // Mock axios response: return the 3 first elements according to the pagination parameters
    axios.get.mockResolvedValueOnce(repositories);

    const response = await RepositoryService.getRepositoriesWithFindingsMetadata(20, 0);
    expect(response).toEqual(repositories);
    expect(response).toBeDefined();
    expect(response).not.toBeNull();
    expect(response.data.length).toBe(2);
    expect(response.data[0].project_key).toBe('RESC');
    expect(response.data[0].repository_id).toBe('1');
    expect(response.data[0].repository_name).toBe('test-repo1');
    expect(response.data[0].repository_url).toBe('https://dev.azure.com/org1/xyz/_git/test-repo1');
    expect(response.data[0].vcs_provider).toBe(`${Config.value('azureDevOpsVal')}`);
    expect(response.data[0].true_positive).toBe(1);
    expect(response.data[0].false_positive).toBe(2);
    expect(response.data[0].not_analyzed).toBe(3);
    expect(response.data[0].under_review).toBe(4);
    expect(response.data[0].clarification_required).toBe(5);
    expect(response.data[0].total_findings_count).toBe(15);
    expect(response.total).toBe(100);
    expect(response.limit).toBe(2);
    expect(response.skip).toBe(0);
  });

  it('fetch a set of repositories, invalid result should throw errors', () => {
    // Mock axios response: return an empty array according to the pagination parameters
    axios.get.mockImplementation(() => Promise.resolve({ data: [] }));

    return RepositoryService.getRepositoriesWithFindingsMetadata(5, 4, 'id', false)
      .then((response) => {
        expect(response).toEqual([]);
        expect(response).not.toBeNull();
        expect(response.data.length).toBe(0);
      })
      .catch((error) => {
        expect(error).toBeDefined();
        expect(error).not.toBeNull();
      });
  });
});

describe('getVCSProviders', () => {
  let vcsProviders = [
    `${Config.value('azureDevOpsVal')}`,
    `${Config.value('bitbucketVal')}`,
    `${Config.value('githubPublicVal')}`,
  ];
  describe('when API call is successful', () => {
    it('should return VCS providers', async () => {
      axios.get.mockResolvedValueOnce(vcsProviders);

      const response = await RepositoryService.getVCSProviders();

      expect(response).toEqual(vcsProviders);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(3);
    });
  });

  describe('when API call fails', () => {
    it('should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RepositoryService.getVCSProviders('not_valid')
        .then((response) => {
          expect(response).toEqual([]);
          expect(response).not.toBeNull();
          expect(response.length).toBe(0);
        })
        .catch((error) => {
          expect(error).toBeDefined();
          expect(error).not.toBeNull();
        });
    });
  });
});

describe('getDistinctProjects', () => {
  let allProjects = ['ABC', 'XYZ', 'GRD0000001', 'GRD0000002'];
  let bitbucketProjects = ['ABC', 'XYZ'];
  let adoProjects = ['GRD0000001', 'GRD0000002'];
  let projectNameByRepoName = ['ABC'];
  describe('when API call is successful', () => {
    it('should return all distinct projects', async () => {
      axios.get.mockResolvedValueOnce(allProjects);

      const response = await RepositoryService.getDistinctProjects(null, '');

      expect(response).toEqual(allProjects);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(4);
    });
  });

  describe('when API call is successful', () => {
    it('should return all distinct bitbucket projects', async () => {
      axios.get.mockResolvedValueOnce(bitbucketProjects);

      const response = await RepositoryService.getDistinctProjects(
        [`${Config.value('bitbucketVal')}`],
        ''
      );

      expect(response).toEqual(bitbucketProjects);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(2);
    });
  });

  describe('when API call is successful', () => {
    it('should return all distinct azure devops projects', async () => {
      axios.get.mockResolvedValueOnce(adoProjects);

      const response = await RepositoryService.getDistinctProjects(
        [`${Config.value('azureDevOpsVal')}`],
        ''
      );

      expect(response).toEqual(adoProjects);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(2);
    });
  });

  describe('when API call is successful', () => {
    it('should return all distinct bitbucket projects for selected project and repository name', async () => {
      axios.get.mockResolvedValueOnce(projectNameByRepoName);

      const response = await RepositoryService.getDistinctProjects(
        [`${Config.value('bitbucketVal')}`],
        'repository-A'
      );

      expect(response).toEqual(projectNameByRepoName);
      expect(response).toBeDefined();
      expect(response).not.toBeNull();
      expect(response.length).toBe(1);
    });
  });

  describe('when API call fails', () => {
    it('should return error', async () => {
      axios.get.mockResolvedValueOnce([]);

      await RepositoryService.getDistinctProjects('not_valid')
        .then((response) => {
          expect(response).toEqual([]);
          expect(response).not.toBeNull();
          expect(response.length).toBe(0);
        })
        .catch((error) => {
          expect(error).toBeDefined();
          expect(error).not.toBeNull();
        });
    });
  });
});
