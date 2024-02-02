import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/ScanFindings/AuditTab.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import status from '@/../tests/resources/mock_status.json';
import findings from '@/../tests/resources/mock_findings.json';
import { BTab, BFormGroup, BFormSelect, BFormTextarea, BButton } from 'bootstrap-vue-next';

vi.mock('axios');

describe('Audit Tab', () => {
  it('display an audit', async () => {
    // Mock axios response
    axios.get.mockResolvedValueOnce(status);
    axios.post.mockResolvedValueOnce({});

    const wrapper = mount(App, {
      props: {
        finding: findings.data[0],
      },
      components: {
        BTab,
        BFormGroup,
        BFormSelect,
        BFormTextarea,
        BButton,
        SpinnerVue,
      },
    });

    expect(wrapper.vm.loadedData).toBe(false);
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.loadedData).toBe(true);
    expect(wrapper.vm.checkFormValidity()).toBe(true);
    expect(() => wrapper.vm.onReset(new Event('reset'))).not.toThrow();
    expect(() => wrapper.vm.onSubmit(new Event('submit'))).not.toThrow();
  });
});
