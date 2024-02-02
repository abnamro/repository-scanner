import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/ScanFindings/HistoryTab.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import audits from '@/../tests/resources/mock_finding_audits.json';
import findings from '@/../tests/resources/mock_findings.json';
import { BTab, BTable, BFormGroup, BFormSelect, BFormTextarea, BButton } from 'bootstrap-vue-next';

vi.mock('axios');

describe('History Tab', () => {
  it('Display an Audit in the History tab', async () => {
    // Mock axios response
    axios.get.mockResolvedValueOnce({ data: audits });

    const wrapper = mount(App, {
      props: {
        finding: findings.data[0],
      },
      components: {
        BTab,
        BFormGroup,
        BFormSelect,
        BFormTextarea,
        BTable,
        BButton,
        SpinnerVue,
      },
    });

    expect(wrapper.vm.loadedData).toBe(false);

    expect(() => wrapper.vm.fetchAuditsForFinding()).not.toThrow();
  });
});
