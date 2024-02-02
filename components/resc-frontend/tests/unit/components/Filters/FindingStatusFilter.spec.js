import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/Filters/FindingStatusFilter.vue';
import mock_statuses from '@/../tests/resources/mock_status.json';
import { BFormGroup } from 'bootstrap-vue-next';
import Multiselect from 'vue-multiselect';
import CommonUtils from '@/utils/common-utils';

vi.mock('axios');

describe('FindingStatusFilter tests', () => {
  it('Given a FindingStatusFilter then FindingStatusFilter will be displayed', () => {
    axios.get.mockResolvedValueOnce(mock_statuses);

    const wrapper = mount(App, {
      props: {},
      components: {
        BFormGroup: BFormGroup,
        Multiselect: Multiselect,
      },
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.findComponent(Multiselect).exists()).toBe(true);
    expect(() => wrapper.vm.onStatusFilterChange()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-findings-status-change');
  });

  it('Given a FindingStatusFilter then FindingStatusFilter will be displayed', async () => {
    axios.get.mockResolvedValueOnce(mock_statuses);

    const wrapper = mount(App, {
      props: {
        statusSelected: [
          {
            id: 0,
            label: CommonUtils.formatStatusLabels('NOT_ANALYZED'),
            value: 'NOT_ANALYZED',
          },
        ],
      },
      components: {
        BFormGroup: BFormGroup,
        Multiselect: Multiselect,
      },
    });

    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onStatusFilterChange()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-findings-status-change');
  });
});
