import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/views/RulePacks.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import Pagination from '@/components/Common/PaginationVue.vue';
import { BTable, BButton } from 'bootstrap-vue-next';
import RulePackUploadModal from '@/components/RulePack/RulePackUploadModal.vue';
import rule_packs from '@/../tests/resources/mock_rule_packs.json';
import { importFA } from '@/assets/font-awesome';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

importFA();

vi.mock('axios');
vi.mock('windows');
describe('RulePacks tests', () => {
  let wrapper;

  axios.get.mockResolvedValueOnce({ data: rule_packs });

  function initMountApp() {
    wrapper = mount(App, {
      props: {},
      components: {
        SpinnerVue,
        Pagination,
        BTable,
        BButton,
        FontAwesomeIcon,
        RulePackUploadModal,
      },
    });
  }

  afterAll(() => {
    console.log.mockRestore();
  });

  afterEach(() => {
    console.log.mockClear();
  });

  it('Given a RulePacks then RulePacks will be displayed', async () => {
    initMountApp();
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.vm.formatDate(0)).toBe('Not Available');
    expect(wrapper.vm.formatDate(123456)).toContain('Jan 01, 1970');
    expect(() => wrapper.vm.showRulePackUploadModal()).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: rule_packs });
    expect(() => wrapper.vm.handlePageClick(1)).not.toThrow();
    axios.get.mockResolvedValueOnce({ data: rule_packs });
    expect(() => wrapper.vm.handlePageSizeChange(20)).not.toThrow();
    axios.get.mockResolvedValueOnce({ data: rule_packs });
    expect(() => wrapper.vm.onRulePackUploadSuccess()).not.toThrow();

    const buffer = new ArrayBuffer();
    axios.get.mockResolvedValueOnce(buffer);
    const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
    expect(() => wrapper.vm.downloadRulePack('0.0.6')).not.toThrow();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    expect(spy).toHaveBeenCalledTimes(2);
  });
});
