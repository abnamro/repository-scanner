import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/components/Filters/RepositoriesPageFilter.vue';
import { BFormCheckbox } from 'bootstrap-vue-next';

describe('RepositoriesPageFilter tests', () => {
  function getApp() {
    return mount(App, {
      props: {
        projectOptions: ['project1', 'project2'],
        repositoryOptions: ['repo1', 'repo2'],
      },
      components: {
        BFormCheckbox: BFormCheckbox,
      },
      global: {
        stubs: {
          VcsProviderFilter: true,
          ProjectFilter: true,
          RepositoryFilter: true,
        },
      },
    });
  }

  it('Given a RepositoriesPageFilter When props are passed then RepositoriesPageFilter will be displayed', () => {
    const wrapper = getApp();
    expect(wrapper.exists()).toBe(true);
  });

  it('Given a RepositoriesPageFilter When props are passed and Project change then event is emitted.', () => {
    const wrapper = getApp();
    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onProjectChange(['project1'])).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
  });

  it('Given a RepositoriesPageFilter When props are passed and Repo change then event is emitted.', () => {
    const wrapper = getApp();
    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onRepositoryChange(['repo1'])).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
  });

  it('Given a RepositoriesPageFilter When props are passed and VCS change then event is emitted.', () => {
    const wrapper = getApp();
    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onVcsProviderChange(['AZURE_DEVOPS'])).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
  });

  it('Given a RepositoriesPageFilter When props are passed and Toggle then event is emitted.', () => {
    const wrapper = getApp();
    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.toggleIncludeZeroFindingRepos()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
  });
});
