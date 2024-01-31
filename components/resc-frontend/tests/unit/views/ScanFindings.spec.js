import { mount } from '@vue/test-utils';
import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import App from '@/views/ScanFindings.vue';
import repositories from '@/../tests/resources/mock_repositories.json';
import vcs_providers from '@/../tests/resources/mock_vcs_providers.json';
import detailed_findings from '@/../tests/resources/mock_detailed_findings.json';
import Pagination from '@/components/Common/PaginationVue.vue';
import FindingStatusBadge from '@/components/Common/FindingStatusBadge.vue';
import RepositoryPanel from '@/components/ScanFindings/RepositoryPanel.vue';
import ScanFindingsService from '@/services/scan-findings-service';
import ScanTypeBadge from '@/components/Common/ScanTypeBadge.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import { BFormCheckbox, BButton } from 'bootstrap-vue-next';
import { importFA } from '@/assets/font-awesome';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

importFA();

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

describe('ScanFindings tests', () => {
  let wrapper;

  const scan = {
    scan_type: 'BASE',
    last_scanned_commit: '1fb42a9ee177ed8141a4ab162a3e33952a4cf6c0',
    timestamp: '2023-05-23T15:52:22.270000',
    increment_number: 0,
    rule_pack: '1.0.0',
    repository_id: 1,
    id_: 1,
  };

  function initMountApp() {
    wrapper = mount(App, {
      props: {
        scanId: '1',
      },
      components: {
        SpinnerVue,
        FindingStatusBadge,
        RepositoryPanel,
        ScanFindingsService,
        ScanTypeBadge,
        Pagination,
        BButton,
        BFormCheckbox,
        FontAwesomeIcon,
      },
      global: {
        stubs: {
          AuditModal: true,
          ScanFindingsFilter: true,
          RepositoriesPageFilter: true,
          FindingPanel: true,
          BTable: true,
        },
      },
    });
  }

  it('Given a ScanFindings then ScanFindings will be displayed', () => {
    axios.get.mockResolvedValueOnce({ data: scan });
    axios.get.mockResolvedValueOnce({ data: repositories });
    axios.get.mockResolvedValueOnce(vcs_providers);

    initMountApp();
    expect(wrapper.exists()).toBe(true);
    expect(() => wrapper.vm.selectSingleCheckbox()).not.toThrow();
    expect(() => wrapper.vm.selectAllCheckboxes()).not.toThrow();
    expect(() => wrapper.vm.onPreviousScanChecked(true)).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.displayPreviousScans([], [], [], [])).not.toThrow();
    expect(() => wrapper.vm.onPreviousScanChecked(false)).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: scan });
    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.handlePageSizeChange(10)).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: scan });
    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.handlePageClick(1)).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: scan });
    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.handleFilterChange(1, ['rule1'], ['NOT_ANALYZED'], [])).not.toThrow();

    axios.get.mockResolvedValueOnce({ data: scan });
    axios.get.mockResolvedValueOnce({ data: detailed_findings });
    expect(() => wrapper.vm.updateAudit('NOT_ANALYZED', 'Rien a declarer')).not.toThrow();
  });
});
