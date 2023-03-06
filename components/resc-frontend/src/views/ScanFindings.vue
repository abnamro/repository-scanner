<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">SCAN FINDINGS</small></h3>
    </div>

    <!-- Spinner -->
    <Spinner :active="spinnerActive" />

    <!-- Repository Panel -->
    <div class="col-md-3 ml-3 mt-4 text-left">
      <RepositoryPanel
        :repository="{
          project_key: repository.project_key,
          repository_name: repository.repository_name,
          vcs_instance_name: vcsInstance.name,
        }"
      ></RepositoryPanel>
    </div>

    <div>
      <!-- Button to audit multiple findings -->
      <b-button
        class="float-left ml-3 audit-btn"
        variant="prime"
        size="sm"
        @click="showAuditModal()"
        :disabled="auditButtonDisabled"
        >AUDIT</b-button
      >
      <AuditModal
        ref="auditModal"
        :selectedCheckBoxIds="selectedCheckBoxIds"
        @update-audit="updateAudit"
      />

      <!-- Filters -->
      <ScanFindingsFilter
        :repository="repository"
        @on-filter-change="handleFilterChange"
        @previous-scans-checked="onPreviousScanChecked"
        @include-previous-scans="displayPreviousScans"
      ></ScanFindingsFilter>
    </div>

    <!--Scan Findings Table -->
    <div v-if="!hasRecords" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <div class="p-3" v-if="hasRecords">
      <b-table
        id="scan-findings-table"
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
          >
          </b-form-checkbox>
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

        <!-- Path Column -->
        <template #cell(file_path)="data">
          {{ data.item.file_path | truncate(45, '...') }}
        </template>

        <!-- Line Column -->
        <template #cell(line_number)="data">
          {{ data.item.line_number }}
        </template>

        <!-- Position Column -->
        <template #cell(position)="data">
          {{ data.item.column_start }} - {{ data.item.column_end }}
        </template>

        <!-- Status Column -->
        <template #cell(status)="data">
          <FindingStatusBadge :status="data.item.status" />
        </template>

        <!-- Remaining Columns (Rule) -->
        <template #cell()="data">
          {{ data.value }}
        </template>

        <!-- Scan Type Column -->
        <template #cell(scanType)="data">
          <ScanTypeBadge
            :scanType="data.item.scanType"
            :incrementNumber="data.item.incrementNumber"
          />
        </template>

        <!-- Expand Table Row To Display Finding Panel -->
        <template v-slot:row-details="{ item }">
          <FindingPanel :finding="item" :repository="repository"></FindingPanel>
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
import AxiosConfig from '@/configuration/axios-config.js';
import Config from '@/configuration/config';
import FindingPanel from '@/components/ScanFindings/FindingPanel.vue';
import FindingStatusBadge from '@/components/Common/FindingStatusBadge.vue';
import Pagination from '@/components/Common/Pagination.vue';
import RepositoryPanel from '@/components/ScanFindings/RepositoryPanel.vue';
import ScanFindingsFilter from '@/components/Filters/ScanFindingsFilter.vue';
import ScanFindingsService from '@/services/scan-findings-service';
import ScanTypeBadge from '@/components/Common/ScanTypeBadge.vue';
import Spinner from '@/components/Common/Spinner.vue';
import spinnerMixin from '@/mixins/spinner.js';
import FindingsService from '@/services/findings-service';
import VCSInstanceService from '@/services/vcs-instance-service';

export default {
  name: 'ScanFindings',
  mixins: [spinnerMixin],
  props: {
    scanId: {},
  },
  data() {
    return {
      previousScanChecked: false,
      scanType: '',
      previousScanList: [],
      incrementNumber: null,
      repositoryId: null,
      branchName: '',
      branchId: null,
      repository: {},
      vcsInstance: {},
      selectedCheckBoxIds: [],
      allSelected: false,
      findingList: [],
      currentItems: [],
      selectedScanID: null,
      ruleFilter: null,
      statusFilter: null,
      totalRows: 0,
      currentPage: 1,
      perPage: Number(`${Config.value('defaultPageSize')}`),
      pageSizes: [20, 50, 100],
      requestedPageNumber: 1,
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
          key: 'rule_name',
          sortable: true,
          label: 'Rule',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'file_path',
          sortable: true,
          label: 'File Path',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'line_number',
          sortable: false,
          label: 'Line',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'position',
          sortable: true,
          label: 'Position',
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
        {
          key: 'scanType',
          sortable: true,
          label: 'Scan Type',
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
    onPreviousScanChecked(checked) {
      this.previousScanChecked = checked;
    },
    handlePageClick(page) {
      this.allSelected = false;
      this.currentPage = page;
      this.previousScanChecked
        ? this.fetchPreviousScanFindings()
        : this.fetchPaginatedFindingsByScanId();
    },
    handlePageSizeChange(pageSize) {
      this.perPage = Number(pageSize);
      this.currentPage = 1;
      this.previousScanChecked
        ? this.fetchPreviousScanFindings()
        : this.fetchPaginatedFindingsByScanId();
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
    fetchVCSInstance() {
      VCSInstanceService.getVCSInstance(this.repository.vcs_instance)
        .then((res) => {
          this.vcsInstance = res.data;
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchRepository() {
      ScanFindingsService.getRepositoryById(this.repositoryId)
        .then((response) => {
          this.repository = response.data;
          this.repository.branch_name = this.branchName;
          this.fetchVCSInstance();
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchScan() {
      this.showSpinner();
      this.selectedScanID = this.scanId;
      ScanFindingsService.getScanById(this.selectedScanID)
        .then((response) => {
          this.branchId = response.data.branch_id;
          this.scanType = response.data.scan_type;
          this.incrementNumber = response.data.increment_number;
          this.fetchBranch();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchBranch() {
      ScanFindingsService.getBranchById(this.branchId)
        .then((response) => {
          this.repositoryId = response.data.repository_id;
          this.branchName = response.data.branch_name;
          this.fetchRepository();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchPaginatedFindingsByScanId() {
      this.showSpinner();
      ScanFindingsService.getScanById(this.selectedScanID)
        .then((response) => {
          this.scanType = response.data.scan_type;
          this.incrementNumber = response.data.increment_number;
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
      const filterObj = {};
      filterObj.skip = this.skipRowCount;
      filterObj.limit = this.perPage;
      filterObj.scanIds = [this.selectedScanID];
      filterObj.findingStatus = this.statusFilter;
      filterObj.rule = this.ruleFilter;

      FindingsService.getDetailedFindings(filterObj)
        .then((response) => {
          this.totalRows = 0;
          this.findingList = [];
          this.selectedCheckBoxIds = [];
          this.totalRows = response.data.total;
          this.findingList = response.data.data;
          this.addScanTypeTagForSingleScan();
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    addScanTypeTagForSingleScan() {
      this.findingList.forEach((finding) => {
        finding.scanType = this.scanType;
        finding.incrementNumber = this.incrementNumber;
      });
    },
    showAuditModal() {
      this.$refs.auditModal.show();
    },
    updateAudit(status, comment) {
      this.findingList.forEach((finding) => {
        if (this.selectedCheckBoxIds.includes(finding.id_)) {
          finding.status = status;
          finding.comment = comment;
        }
      });
      this.fetchPaginatedFindingsByScanId();
      this.allSelected = false;
    },
    handleFilterChange(scanId, rule, status) {
      this.selectedScanID = scanId;
      this.ruleFilter = rule;
      this.statusFilter = status;
      this.currentPage = 1;
      this.allSelected = false;
      this.fetchPaginatedFindingsByScanId();
    },
    displayPreviousScans(rule, status, previousScanList) {
      this.currentPage = 1;
      this.allSelected = false;
      this.previousScanList = previousScanList;
      this.ruleFilter = rule;
      this.statusFilter = status;
      this.fetchPreviousScanFindings();
    },
    fetchPreviousScanFindings() {
      const previousScanIds = [];
      for (const scan of this.previousScanList) {
        previousScanIds.push(scan.id_);
      }

      this.showSpinner();

      const filterObj = {};
      filterObj.skip = this.skipRowCount;
      filterObj.limit = this.perPage;
      filterObj.scanIds = previousScanIds;
      filterObj.findingStatus = this.statusFilter;
      filterObj.rule = this.ruleFilter;

      FindingsService.getDetailedFindings(filterObj)
        .then((response) => {
          this.totalRows = 0;
          this.findingList = [];
          this.selectedCheckBoxIds = [];
          this.totalRows = response.data.total;
          this.findingList = response.data.data;
          this.addScanTypeTagForMultipleScans();
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    addScanTypeTagForMultipleScans() {
      this.previousScanList.forEach((scan) => {
        this.findingList.forEach((finding) => {
          if (scan.id_ === finding.scan_id) {
            finding.scanType = scan.scan_type;
            finding.incrementNumber = scan.increment_number;
          }
        });
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
    this.fetchScan();
  },
  components: {
    AuditModal,
    FindingPanel,
    FindingStatusBadge,
    Pagination,
    RepositoryPanel,
    ScanFindingsFilter,
    ScanTypeBadge,
    Spinner,
  },
};
</script>
