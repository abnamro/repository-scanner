import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/views/RepositoriesPanel.vue';
import repositories from '@/../tests/resources/mock_repositories.json';
import vcs_providers from '@/../tests/resources/mock_vcs_providers.json';
import HealthBar from '@/components/Common/HealthBar.vue';
import Pagination from '@/components/Common/PaginationVue.vue';
import RepositoriesPageFilter from '@/components/Filters/RepositoriesPageFilter.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import { BTable } from 'bootstrap-vue-next';

vi.mock('axios');
const allRepos = ['bb_repo1', 'bb_repo2', 'ado_repo1', 'ado_repo2'];
// const bitbucketRepos = ['bb_repo1', 'bb_repo2'];
// const adoRepos = ['ado_repo1', 'ado_repo2'];

const allProjects = ['ABC', 'XYZ', 'GRD0000001', 'GRD0000002'];
// const bitbucketProjects = ['ABC', 'XYZ'];
// const adoProjects = ['GRD0000001', 'GRD0000002'];
// const projectNameByRepoName = ['ABC'];

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router');
  return {
    ...actual,
    useRoute: vi.fn(),
    useRouter: vi.fn(() => ({
      push: () => {},
    })),
  };
});

describe('RepositoriesPanel tests', () => {
  let wrapper;

  function initMountApp() {
    wrapper = mount(App, {
      components: {
        SpinnerVue,
        HealthBar,
        Pagination,
        RepositoriesPageFilter,
        BTable,
      },
      global: {
        stubs: {
          // RepositoriesPageFilter: true
        },
      },
    });
  }

  it('Given a RepositoriesPanel then RepositoriesPanel will be displayed', () => {
    axios.get.mockResolvedValueOnce({ data: allProjects });
    axios.get.mockResolvedValueOnce({ data: allRepos });
    axios.get.mockResolvedValueOnce(vcs_providers);
    axios.get.mockResolvedValueOnce({ data: repositories });
    // Repository Page Filter

    initMountApp();
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.vm.formatDate(0)).toBe('Not Scanned');
    expect(wrapper.vm.formatDate(123456)).toContain('Jan 01, 1970');
    expect(wrapper.vm.formatVcsProvider('GITHUB_PUBLIC')).toBe('GitHub Public');

    axios.get.mockResolvedValueOnce({ data: repositories });
    wrapper.vm.handlePageClick(1);
    axios.get.mockResolvedValueOnce({ data: repositories });
    wrapper.vm.handlePageSizeChange(1);
    axios.get.mockResolvedValueOnce({ data: allProjects });
    axios.get.mockResolvedValueOnce({ data: allRepos });
    axios.get.mockResolvedValueOnce({ data: repositories });
    wrapper.vm.handleFilterChange(['AZURE_DEVOPS'], undefined, undefined);
  });
});
