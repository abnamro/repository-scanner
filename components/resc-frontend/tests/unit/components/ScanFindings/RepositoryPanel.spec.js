import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/components/ScanFindings/RepositoryPanel.vue';

describe('Repository Panel', () => {
  it('Display dummy data in a Repository Panel', () => {
    const wrapper = mount(App, {
      props: {
        repository: { project_key: 'project_name', repository_name: 'repo_name' },
        vcs_instance: { name: 'vcs_name' },
      },
      components: {},
    });

    expect(wrapper.text()).toContain('project_name');
    expect(wrapper.text()).toContain('repo_name');
    expect(wrapper.text()).toContain('vcs_name');
  });
});
