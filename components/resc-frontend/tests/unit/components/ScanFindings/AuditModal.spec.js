import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/ScanFindings/AuditModal.vue';
import status from '@/../tests/resources/mock_status.json';
import { BTab, BFormGroup, BFormSelect, BFormTextarea, BButton } from 'bootstrap-vue-next';

vi.mock('axios');

describe('Audit Modal', () => {
  it('fetch a audit', async () => {
    // Mock axios response
    axios.get.mockResolvedValueOnce(status);
    axios.post.mockResolvedValueOnce({});

    const wrapper = mount(App, {
      props: {
        selectedCheckBoxIds: [1, 2, 3, 4, 5],
      },
      components: {
        BTab,
        BFormGroup,
        BFormSelect,
        BFormTextarea,
        BButton,
      },
    });

    expect(wrapper.vm.isStatusValid).toBe(true);
    expect(wrapper.vm.getModalTitle).toBe('AUDIT 5 FINDINGS');
    expect(wrapper.vm.isCommentValid).toBe(true);
    expect(() => wrapper.vm.show()).not.toThrow();
    expect(() => wrapper.vm.hide()).not.toThrow();
    expect(() => wrapper.vm.resetModal()).not.toThrow();
    expect(() => wrapper.vm.handleOk(new MouseEvent('click'))).not.toThrow();
  });
});
