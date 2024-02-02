import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/Metrics/RuleMetrics.vue';
import { BTable } from 'bootstrap-vue-next';
import rule_packs from '@/../tests/resources/mock_rule_packs.json';
import rule_tags from '@/../tests/resources/mock_rule_tags.json';
import rules_with_findings_status_count from '@/../tests/resources/mock_rules_with_findings_status_count.json';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import { createApp } from 'vue';
import { PiniaVuePlugin, createPinia, setActivePinia } from 'pinia';

const app = createApp({});
const pinia = createPinia();
setActivePinia(pinia);
app.use(PiniaVuePlugin);

vi.mock('axios');
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

describe('RuleMetrics tests', () => {
  it('Given a RuleMetrics When props are passed then RuleMetrics will be displayed', async () => {
    axios.get.mockResolvedValueOnce({ data: rule_packs });
    axios.get.mockResolvedValueOnce(rule_tags);
    axios.get.mockResolvedValueOnce({ data: rules_with_findings_status_count });

    const wrapper = mount(App, {
      props: {},
      components: {
        BTable: BTable,
        SpinnerVue: SpinnerVue,
      },
      global: {
        stubs: {
          HealthBar: true,
          RulePackFilter: true,
          RuleTagsFilter: true,
        },
      },
    });

    expect(wrapper.exists()).toBe(true);
    // We need to wait a few ticks for the re-rendering of the wrapper.
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick();
    await wrapper.vm.$nextTick(); // Re-rendiring table
    expect(wrapper.vm.loadedData).toBe(true);
    expect(wrapper.vm.ruleList.length > 0).toBe(true);
    expect(wrapper.vm.hasRecords).toBe(true);

    wrapper.find('tr').trigger('click');
    wrapper.vm.goToRuleAnalysisPage({ rule_name: 'Rule-3' });
  });

  it('Given a RuleMetrics When props are passed then RuleMetrics will be displayed', () => {
    axios.get.mockResolvedValueOnce({ data: rule_packs });
    axios.get.mockResolvedValueOnce(rule_tags);
    axios.get.mockResolvedValueOnce({ data: rules_with_findings_status_count });

    const wrapper = mount(App, {
      props: {
        rulePackVersion: [{ version: '0.0.6', active: true, created: 'today' }],
      },
      components: {
        BTable: BTable,
        SpinnerVue: SpinnerVue,
      },
      global: {
        stubs: {
          HealthBar: true,
          RulePackFilter: true,
          RuleTagsFilter: true,
        },
      },
    });

    expect(wrapper.exists()).toBe(true);
    axios.get.mockResolvedValueOnce(rule_tags);
    axios.get.mockResolvedValueOnce({ data: rules_with_findings_status_count });
    wrapper.vm.onRulePackVersionChange(['0.0.5']);

    axios.get.mockResolvedValueOnce({ data: rules_with_findings_status_count });
    wrapper.vm.onRuleTagsFilterChange(['Info']);
  });
});
