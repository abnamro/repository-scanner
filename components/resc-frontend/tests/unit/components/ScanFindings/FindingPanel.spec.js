import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/components/ScanFindings/FindingPanel.vue';
import finding from '@/../tests/resources/mock_detailed_findings.json';
import { BTab, BCardText } from 'bootstrap-vue-next';

describe('FindingPanel Tab', () => {
  it('display a finding', async () => {
    const wrapper = mount(App, {
      props: {
        finding: finding.data[0],
      },
      components: {
        BTab,
        BCardText,
      },
      global: {
        stubs: {
          AuditTab: true,
          HistoryTab: true,
        },
      },
    });
    expect(wrapper.html()).toContain('roles/fixgate/defaults/main.yml');
  });
});
