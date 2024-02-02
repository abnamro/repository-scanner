import { shallowMount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/components/Filters/RuleAnalysisFilter.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { BCollapse, BButton } from 'bootstrap-vue-next';
import { createTestingPinia } from '@pinia/testing';
import rules from '@/../tests/resources/mock_rules.json';
import rule_tags from '@/../tests/resources/mock_rule_tags.json';

vi.mock('axios');

// RuleService.getAllDetectedRules
// RulePackService.getRuleTagsByRulePackVersions
describe('RuleAnalysisFilter tests', () => {
  function initMount() {
    return shallowMount(App, {
      props: {},
      components: {
        BButton: BButton,
        BCollapse: BCollapse,
        FontAwesomeIcon: FontAwesomeIcon,
      },
      global: {
        plugins: [
          createTestingPinia({
            stubActions: false,
            initialState: {
              authUser: {
                idToken: '12345',
                accessToken: '12345',
                destinationRoute: 'resc',
                firstName: 'user',
                lastName: 'test',
                email: 'testuser@test.com',
              },
            },
          }),
        ],
      },
    });
  }

  it('Given a RuleAnalysisFilter then RuleAnalysisFilter will be displayed', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);
    axios.get.mockReset();
  });

  it('Given a RuleAnalysisFilter When updating VCS filters then on-filter-change is emitted', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);

    axios.get.mockResolvedValueOnce({ data: rules });
    expect(() => wrapper.vm.onVcsProviderChange(['AZURE_DEVOPS'])).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
    axios.get.mockReset();
  });

  it('Given a RuleAnalysisFilter When updating Project filters then on-filter-change is emitted', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });
    axios.get.mockResolvedValueOnce({ data: rules });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);

    expect(() => wrapper.vm.onProjectChange('ABC')).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
    axios.get.mockReset();
  });

  it('Given a RuleAnalysisFilter When updating Repo filters then on-filter-change is emitted', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);

    axios.get.mockResolvedValueOnce({ data: rules });
    expect(() => wrapper.vm.onRepositoryChange('Repo1')).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
    axios.get.mockReset();
  });

  it('Given a RuleAnalysisFilter When updating FindingStatus filters then on-filter-change is emitted', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);

    axios.get.mockResolvedValueOnce({ data: rules });
    expect(() => wrapper.vm.onFindingsStatusChange(['NOT_ANALYZED'])).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
    axios.get.mockReset();
  });

  it('Given a RuleAnalysisFilter When updating Rule filters then on-filter-change is emitted', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onRuleChange(['Rule-1'])).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
    axios.get.mockReset();
  });

  it('Given a RuleAnalysisFilter When updating RuleTag filters then on-filter-change is emitted', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.onRuleTagsChange(['Info'])).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
    axios.get.mockReset();
  });

  it('Given a RuleAnalysisFilter When updating RulePack filters then on-filter-change is emitted', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);

    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });
    expect(() => wrapper.vm.onRulePackVersionChange(['0.0.5'])).not.toThrow();
    expect(wrapper.emitted()).toHaveProperty('on-filter-change');
    axios.get.mockReset();
  });

  it('Given a RuleAnalysisFilter When updating RulePack filters then on-filter-change is emitted', () => {
    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });

    const wrapper = initMount();
    expect(wrapper.exists()).toBe(true);

    axios.get.mockResolvedValueOnce({ data: rules });
    axios.get.mockResolvedValueOnce({ rule_tags });
    expect(() => wrapper.vm.setRulePackVersionsOnRulePackFilter(['0.0.5'])).not.toThrow();
    axios.get.mockReset();
  });
});
