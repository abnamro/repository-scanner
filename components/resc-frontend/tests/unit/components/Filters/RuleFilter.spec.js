import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import App from '@/components/Filters/RuleFilter.vue';
import { BFormGroup } from 'bootstrap-vue-next';
import Multiselect from 'vue-multiselect';

describe('RuleFilter tests', () => {
  function getApp() {
    return mount(App, {
      props: {
        rulesOptions: ['rule1', 'rule2'],
        rulesSelected: [],
      },
      components: {
        BFormGroup: BFormGroup,
        Multiselect: Multiselect,
      },
    });
  }

  it('Given a RuleFilter When props are passed then RuleFilter will be displayed', () => {
    const wrapper = getApp();
    expect(wrapper.exists()).toBe(true);
  });

  it('Given a RuleFilter When props are passed and Rule change then evetn is emitted', async () => {
    const wrapper = getApp();
    expect(wrapper.exists()).toBe(true);
    wrapper.setProps({ rulesSelected: ['rule3'] });
    await wrapper.vm.$nextTick();
    expect(() => wrapper.vm.onRuleFilterChange()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-rule-change');
  });

  it('Given a RuleFilter When props are passed and Rule change then evetn is emitted', () => {
    const wrapper = getApp();
    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.resetRuleFilterSelection()).not.toThrow();
    expect(() => wrapper.vm.onRuleFilterChange()).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-rule-change');
  });
});
