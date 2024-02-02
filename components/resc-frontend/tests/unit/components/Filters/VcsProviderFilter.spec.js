import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/Filters/VcsProviderFilter.vue';
import Config from '@/configuration/config';
import Multiselect from 'vue-multiselect';
import { BFormGroup } from 'bootstrap-vue-next';
import vcs_providers from '@/../tests/resources/mock_vcs_providers.json';

vi.mock('axios');

describe('VcsProviderFilter tests', () => {
  it('Given a VcsProviderFilter When props are passed then VcsProviderFilter will be displayed', () => {
    axios.get.mockResolvedValueOnce(vcs_providers);

    const wrapper = mount(App, {
      props: {},
      components: {
        Multiselect,
        BFormGroup,
      },
    });

    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onVcsFilterChange()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-vcs-change');
  });

  it('Given a VcsProviderFilter When props are passed then VcsProviderFilter will be displayed', () => {
    axios.get.mockResolvedValueOnce(vcs_providers);

    const wrapper = mount(App, {
      props: {
        vcsProvidersSelected: [
          {
            id: 0,
            value: 'AZURE_DEVOPS',
            label: `${Config.value('azureDevOpsVal')}`,
          },
        ],
      },
      components: {
        Multiselect,
        BFormGroup,
      },
    });

    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onVcsFilterChange()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-vcs-change');
  });
});
