import { shallowMount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/views/RuleAnalysis.vue';
import { importFA } from '@/assets/font-awesome';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { createTestingPinia } from '@pinia/testing';
import { BFormCheckbox, BButton } from 'bootstrap-vue-next';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import Pagination from '@/components/Common/PaginationVue.vue';
import rule_packs from '@/../tests/resources/mock_rule_packs.json';
import detailed_findings from '@/../tests/resources/mock_detailed_findings.json';

let allProjects = ['ABC', 'XYZ', 'GRD0000001', 'GRD0000002'];
let allRepos = ['bb_repo1', 'bb_repo2', 'ado_repo1', 'ado_repo2'];

importFA();

vi.mock('axios');

describe('RuleAnalysis tests', () => {
  it('Given a RuleAnalysis then RuleAnalysis will be displayed', () => {
    axios.get.mockResolvedValueOnce({ data: rule_packs });
    axios.get.mockResolvedValueOnce({ data: allProjects });
    axios.get.mockResolvedValueOnce({ data: allRepos });
    axios.get.mockResolvedValueOnce({ data: detailed_findings });

    const wrapper = shallowMount(App, {
      components: {
        SpinnerVue,
        Pagination,
        BButton,
        BFormCheckbox,
        FontAwesomeIcon,
      },
      global: {
        plugins: [createTestingPinia()],
        stubs: {
          AuditModal: true,
          RuleAnalysisFilter: true,
          RepositoriesPageFilter: true,
          FindingPanel: true,
          BTable: true,
          FindingStatusBadge: true,
        },
      },
    });

    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.selectSingleCheckbox()).not.toThrow();
    expect(() => wrapper.vm.selectAllCheckboxes()).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.handlePageSizeChange(10)).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.handlePageClick(1)).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.updateAudit('NOT_ANALYZED', 'Rien a declarer')).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.fetchPaginatedDetailedFindings()).not.toThrow();
  });

  it('Given a RuleAnalysis then RuleAnalysis will be displayed', () => {
    axios.get.mockResolvedValueOnce({ data: rule_packs });
    axios.get.mockResolvedValueOnce({ data: allProjects });
    axios.get.mockResolvedValueOnce({ data: allRepos });
    axios.get.mockResolvedValueOnce({ data: detailed_findings });

    const wrapper = shallowMount(App, {
      components: {
        SpinnerVue,
        Pagination,
        BButton,
        BFormCheckbox,
        FontAwesomeIcon,
      },
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              authUser: {
                idToken: '12345',
                accessToken: '12345',
                firstName: 'user',
                lastName: 'test',
                email: 'testuser@test.com',
                sourceRoute: '/metrics/rule-metrics',
                destinationRoute: '/rule-analysis',
                previousRouteState: { rulePackVersions: '0.0.1' },
              },
            },
          }),
        ],
        stubs: {
          AuditModal: true,
          RuleAnalysisFilter: true,
          RepositoriesPageFilter: true,
          FindingPanel: true,
          BTable: true,
        },
      },
    });

    expect(wrapper.exists()).toBe(true);
  });
});
