<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">RULE ANALYSIS</small></h3>
    </div>

    <!-- Spinner -->
    <Spinner :active="spinnerActive" />

    <!-- Filters -->
    <div class="mt-4">
      <RuleAnalysisFilter
        :projectOptions="projectNames"
        :repositoryOptions="repositoryNames"
        :selectedRulePackVersionsList="selectedRulePackVersionsList"
        :rulePackVersions="rulePackVersions"
        @on-filter-change="handleFilterChange"
      ></RuleAnalysisFilter>
    </div>

    <div class="ml-3">
      <!-- Button to audit multiple findings -->
      <b-button
        class="float-left mt-2 mb-2"
        variant="prime"
        size="sm"
        @click="showAuditModal()"
        :disabled="auditButtonDisabled"
        >AUDIT</b-button
      >
      <!-- Audit Modal -->
      <AuditModal
        ref="auditModal"
        :selectedCheckBoxIds="selectedCheckBoxIds"
        @update-audit="updateAudit"
      />
    </div>

    <!--Scan Findings Table -->
    <div v-if="!hasRecords" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <div class="p-3" v-if="hasRecords">
      <b-table
        id="rule-analysis-table"
        sticky-header="85vh"
        :items="findingList"
        :fields="fields"
        :current-page="currentPage"
        :per-page="0"
        primary-key="id_"
        v-model="currentItems"
        responsive
        small
        head-variant="light"
        @row-clicked="toggleFindingDetails"
      >
        <!-- Select all checkboxes -->
        <template #head(select)>
          <b-form-checkbox
            class="checkbox"
            v-model="allSelected"
            @change="selectAllCheckboxes"
          ></b-form-checkbox>
        </template>

        <!-- Selection checkboxes -->
        <template #cell(select)="data">
          <b-form-checkbox
            class="checkbox"
            v-model="selectedCheckBoxIds"
            :value="data.item.id_"
            @change="selectSingleCheckbox"
          ></b-form-checkbox>
        </template>

        <!-- Collapse Icon Column -->
        <template v-slot:cell(toggle_row)="{ detailsShowing }">
          <font-awesome-icon
            size="lg"
            class="collapse-arrow"
            slot="dropdown-icon"
            icon="angle-right"
            :rotation="detailsShowing ? 90 : null"
          />
        </template>

        <!-- Location Column -->
        <template #cell(file_path)="data">
          {{ data.item.file_path | truncate(45, '...') }} #{{ data.item.line_number }}
        </template>

        <!-- Status Column -->
        <template #cell(status)="data">
          <FindingStatusBadge :status="data.item.status" />
        </template>

        <!-- Remaining Columns (Rule) -->
        <template #cell()="data">
          {{ data.value }}
        </template>

        <!-- Expand Table Row To Display Finding Panel -->
        <template v-slot:row-details="{ item }">
          <FindingPanel
            :finding="item"
            :repository="{
              project_key: item.project_key,
              repository_name: item.repository_name,
              repository_url: item.repository_url,
              vcs_provider: item.vcs_provider,
              branch_name: item.branch_name,
            }"
          ></FindingPanel>
        </template>
      </b-table>

      <!-- Pagination -->
      <Pagination
        :currentPage="currentPage"
        :perPage="perPage"
        :totalRows="totalRows"
        :pageSizes="pageSizes"
        :requestedPageNumber="requestedPageNumber"
        @page-click="handlePageClick"
        @page-size-change="handlePageSizeChange"
      ></Pagination>
    </div>
  </div>
</template>

<script>
import AuditModal from '@/components/ScanFindings/AuditModal';
import Config from '@/configuration/config';
import AxiosConfig from '@/configuration/axios-config.js';
import FindingPanel from '@/components/ScanFindings/FindingPanel.vue';
import FindingsService from '@/services/findings-service';
import FindingStatusBadge from '@/components/Common/FindingStatusBadge.vue';
import RepositoryService from '@/services/repository-service';
import Spinner from '@/components/Common/Spinner.vue';
import Pagination from '@/components/Common/Pagination.vue';
import RuleAnalysisFilter from '@/components/Filters/RuleAnalysisFilter.vue';
import RulePackService from '@/services/rule-pack-service';
import spinnerMixin from '@/mixins/spinner.js';
import Store from '@/store/index.js';

export default {
  name: 'RuleAnalysis',
  mixins: [spinnerMixin],
  data() {
    return {
      findingList: [],
      currentItems: [],
      totalRows: 0,
      currentPage: 1,
      perPage: Number(`${Config.value('defaultPageSize')}`),
      pageSizes: [20, 50, 100],
      requestedPageNumber: 1,
      rulePackVersions: [],
      projectNames: [],
      repositoryNames: [],
      selectedStartDate: '',
      selectedEndDate: '',
      selectedVcsProvider: null,
      selectedStatus: null,
      selectedProject: null,
      selectedRepository: null,
      selectedBranch: null,
      selectedRule: null,
      selectedRulePackVersions: [],
      selectedRulePackVersionsList: [],
      selectedCheckBoxIds: [],
      allSelected: false,
      fields: [
        {
          key: 'select',
          label: '',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'toggle_row',
          label: '',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'project_key',
          sortable: true,
          label: 'Project',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'repository_name',
          sortable: true,
          label: 'Repository',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'branch_name',
          sortable: true,
          label: 'Branch',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'rule_name',
          sortable: true,
          label: 'Rule',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'file_path',
          sortable: true,
          label: 'Location',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'status',
          sortable: true,
          label: 'Status',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
      ],
    };
  },
  computed: {
    hasRecords() {
      return this.findingList.length > 0;
    },
    skipRowCount() {
      return (this.currentPage - 1) * this.perPage;
    },
    auditButtonDisabled() {
      return this.selectedCheckBoxIds.length <= 0;
    },
  },
  methods: {
    selectSingleCheckbox() {
      this.allSelected = false;
    },
    selectAllCheckboxes() {
      this.selectedCheckBoxIds = [];
      if (this.allSelected) {
        for (const finding of this.findingList) {
          this.selectedCheckBoxIds.push(finding.id_);
        }
      }
    },
    showAuditModal() {
      this.$refs.auditModal.show();
    },
    handlePageClick(page) {
      this.allSelected = false;
      this.currentPage = page;
      this.fetchPaginatedDetailedFindings();
    },
    handlePageSizeChange(pageSize) {
      this.perPage = Number(pageSize);
      this.currentPage = 1;
      this.fetchPaginatedDetailedFindings();
    },
    toggleFindingDetails(row) {
      if (row._showDetails) {
        this.$set(row, '_showDetails', false);
      } else {
        this.currentItems.forEach((item) => {
          this.$set(item, '_showDetails', false);
        });
        this.$nextTick(() => {
          this.$set(row, '_showDetails', true);
        });
      }
    },
    fetchPaginatedDetailedFindings() {
      this.showSpinner();
      const filterObj = {};
      filterObj.skip = this.skipRowCount;
      filterObj.limit = this.perPage;
      filterObj.startDate = this.selectedStartDate;
      filterObj.endDate = this.selectedEndDate;
      filterObj.vcsProvider = this.selectedVcsProvider;
      filterObj.findingStatus = this.selectedStatus;
      filterObj.project = this.selectedProject;
      filterObj.repository = this.selectedRepository;
      filterObj.branch = this.selectedBranch;
      filterObj.rule = this.selectedRule;
      filterObj.rulePackVersions = this.selectedRulePackVersions;

      FindingsService.getDetailedFindings(filterObj)
        .then((response) => {
          this.totalRows = 0;
          this.findingList = [];
          this.selectedCheckBoxIds = [];
          this.totalRows = response.data.total;
          this.findingList = response.data.data;
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    updateAudit(status, comment) {
      this.findingList.forEach((finding) => {
        if (this.selectedCheckBoxIds.includes(finding.id_)) {
          finding.status = status;
          finding.comment = comment;
        }
      });
      this.allSelected = false;
      this.fetchPaginatedDetailedFindings();
    },
    handleFilterChange(filterObj) {
      this.selectedStartDate = filterObj.startDate;
      this.selectedEndDate = filterObj.endDate;
      this.selectedVcsProvider = filterObj.vcsProvider;
      this.selectedStatus = filterObj.status;
      this.selectedProject = filterObj.project;
      this.selectedRepository = filterObj.repository;
      this.selectedBranch = filterObj.branch;
      this.selectedRule = filterObj.rule;
      this.selectedRulePackVersions = filterObj.rulePackVersions;
      this.currentPage = 1;
      this.allSelected = false;
      this.fetchDistinctProjects();
      this.fetchDistinctRepositories();
      this.fetchPaginatedDetailedFindings();
    },
    fetchDistinctProjects() {
      RepositoryService.getDistinctProjects(this.selectedVcsProvider, this.selectedRepository)
        .then((response) => {
          this.projectNames = [];
          for (const project_key of response.data) {
            this.projectNames.push(project_key);
          }
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchDistinctRepositories() {
      RepositoryService.getDistinctRepositories(this.selectedVcsProvider, this.selectedProject)
        .then((response) => {
          this.repositoryNames = [];
          for (const repo_name of response.data) {
            this.repositoryNames.push(repo_name);
          }
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchRulePackVersions() {
      RulePackService.getRulePackVersions(10000, 0)
        .then((response) => {
          this.rulePackVersions = [];
          this.selectedRulePackVersions = [];
          for (const index of response.data.data.keys()) {
            const rulePackJson = {};
            rulePackJson['id'] = index;
            const data = response.data.data[index];
            if (data.active) {
              rulePackJson['label'] = data.version + ' ' + '(active)';
              this.selectedRulePackVersions.push(data.version);
              this.selectedRulePackVersionsList.push(rulePackJson);
            } else {
              rulePackJson['label'] = data.version;
            }
            this.rulePackVersions.push(rulePackJson);
          }
          //load findings when no filter values are provided from previous route
          if (!Store.getters.previousRouteState) {
            this.fetchPaginatedDetailedFindings();
          }
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
  },
  filters: {
    truncate: function (text, length, suffix) {
      if (text.length > length) {
        return text.substring(0, length) + suffix;
      } else {
        return text;
      }
    },
  },

  created() {
    this.fetchRulePackVersions();
    this.fetchDistinctProjects();
    this.fetchDistinctRepositories();
  },
  components: {
    AuditModal,
    FindingPanel,
    FindingStatusBadge,
    Pagination,
    RuleAnalysisFilter,
    Spinner,
  },
};
</script>
