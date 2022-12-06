<template>
  <div>
    <div class="row">
      <!-- Branch Filter -->
      <div class="col-md-2 ml-3">
        <b-form-group class="label-title text-left" label="Branch" label-for="branch-filter">
          <multiselect
            v-model="selectedBranch"
            :options="branchList"
            :multiple="false"
            :searchable="false"
            :allow-empty="false"
            :show-labels="false"
            label="branch_name"
            track-by="id_"
            :preselect-first="false"
            @input="handleBranchFilterChange"
          >
          </multiselect>
        </b-form-group>
      </div>

      <!-- Scan Date Filter -->
      <div class="col-md-3">
        <b-form-group class="label-title text-left" label="Scan Date" label-for="scan-date-filter">
          <multiselect
            v-model="selectedScan"
            :options="scanDateList"
            :multiple="false"
            :searchable="false"
            :allow-empty="false"
            :show-labels="false"
            :custom-label="formatScanDateFilterOptions"
            track-by="scanId"
            :preselect-first="false"
            @input="handleScanDateFilterChange"
          >
            <template slot="singleLabel" slot-scope="{ option }"
              ><span>{{ formatScanDateFilterOptions(option) }}</span></template
            >
          </multiselect>
        </b-form-group>
      </div>

      <!-- Rule Filter -->
      <div class="col-md-3">
        <RuleFilter :options="ruleList" @on-rule-change="handleRuleFilterChange" />
      </div>

      <!-- Status Filter -->
      <div class="col-md-3">
        <FindingStatusFilter @on-findings-status-change="onStatusFilterChange" />
      </div>
    </div>

    <!-- Include previous scan findings -->
    <div class="row">
      <div class="col-md-2 ml-3">
        <b-form-checkbox
          v-model="includePreviousScans"
          name="check-button"
          switch
          @change="togglePreviousScans"
        >
          <small class="text-nowrap">Include previous scan findings</small>
        </b-form-checkbox>
      </div>
    </div>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import DateUtils from '@/utils/date-utils';
import FindingStatusFilter from '@/components/Filters/FindingStatusFilter.vue';
import Multiselect from 'vue-multiselect';
import RuleFilter from '@/components/Filters/RuleFilter.vue';
import RepositoryService from '@/services/repository-service';
import ScanFindingsService from '@/services/scan-findings-service';

export default {
  name: 'ScanFindingsFilter',
  props: {
    repository: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      previousScans: [],
      branchList: [],
      scanList: [],
      scanDateList: [],
      ruleList: [],
      statusList: [],
      selectedBranch: null,
      selectedScan: null,
      selectedRule: null,
      selectedStatus: null,
      includePreviousScans: false,
    };
  },
  methods: {
    getPreviousScans() {
      for (const scan of this.scanList) {
        if (this.selectedScan.scanId >= scan.id_) {
          this.previousScans.push(scan);
          if (scan.scan_type === 'BASE') {
            break;
          }
        }
      }
    },
    togglePreviousScans() {
      if (this.includePreviousScans) {
        this.previousScans = [];
        this.getPreviousScans();
        this.$emit('previous-scans-checked', true);
        this.$emit(
          'include-previous-scans',
          this.selectedRule,
          this.selectedStatus,
          this.previousScans
        );
      } else {
        this.previousScans = [];
        this.$emit('previous-scans-checked', false);
        this.handleFilterChange();
      }

      // Refresh rules in filter based on scan ids
      this.refreshRuleFilter();
    },
    formatScanDateFilterOptions(scan) {
      return `${scan.scanDate}: ${scan.scanType}`;
    },
    handleBranchFilterChange() {
      this.fetchScanDates();
    },
    handleScanDateFilterChange() {
      this.fetchRules();
    },
    handleRuleFilterChange(rule) {
      this.selectedRule = rule;
      this.handleFilterChange();
    },
    onStatusFilterChange(status) {
      this.selectedStatus = status;
      this.handleFilterChange();
    },
    handleFilterChange() {
      // Refresh findings
      if (!this.includePreviousScans) {
        this.$emit(
          'on-filter-change',
          this.selectedScan.scanId,
          this.selectedRule,
          this.selectedStatus
        );
      } else {
        this.togglePreviousScans();
      }
    },
    getPreviousScanIds() {
      const previousScanIds = [];
      for (const scan of this.previousScans) {
        previousScanIds.push(scan.id_);
      }
      const scanIds = this.includePreviousScans ? previousScanIds : [this.selectedScan.scanId];
      return scanIds;
    },
    refreshRuleFilter() {
      const scanIds = this.getPreviousScanIds();
      if (scanIds.length > 0) {
        ScanFindingsService.getRulesByScanIds(scanIds)
          .then((response) => {
            this.selectedRule = null;
            this.ruleList = response.data;
          })
          .catch((error) => {
            AxiosConfig.handleError(error);
          });
      }
    },
    fetchRules() {
      const scanIds = this.getPreviousScanIds();
      if (this.selectedScan.scanId && scanIds.length > 0) {
        ScanFindingsService.getRulesByScanIds(scanIds)
          .then((response) => {
            this.selectedRule = null;
            this.ruleList = response.data;

            // Refresh findings
            this.handleFilterChange();

            // if scanId gets changed, update it in route parameter
            if (Number(this.$route.params.scanId) !== Number(this.selectedScan.scanId)) {
              this.$router.replace({
                name: 'ScanFindings',
                params: { scanId: this.selectedScan.scanId },
              });
            }
          })
          .catch((error) => {
            AxiosConfig.handleError(error);
          });
      }
    },
    fetchScanDates() {
      if (this.selectedBranch.id_) {
        ScanFindingsService.getScansByBranchId(this.selectedBranch.id_)
          .then((response) => {
            this.scanDateList = [];

            this.scanList = response.data.data.sort(function (a, b) {
              return new Date(b.timestamp) - new Date(a.timestamp);
            });

            for (const scan of response.data.data) {
              const scanJson = {};
              scanJson['scanId'] = scan.id_;
              scanJson['scanDate'] = DateUtils.formatDate(scan.timestamp);
              scanJson['scanType'] = scan.scan_type === 'INCREMENTAL' ? 'Incremental' : 'Base';

              // Set scan date value in select option when user clicks branch scan findings record from Repositories page
              if (this.$route.params.scanId === scan.id_) {
                this.selectedScan = scanJson;
              } else {
                this.selectedScan = null;
              }
              this.scanDateList.push(scanJson);
            }

            //Sort scan dates
            this.scanDateList.sort(DateUtils.sortListByDate);

            // On branch change set scan date value in select option
            if (!this.selectedScan) {
              this.selectedScan = this.scanDateList[0];
            }

            //Rules depend upon scan/scan date selected
            this.fetchRules();
          })
          .catch((error) => {
            AxiosConfig.handleError(error);
          });
      }
    },
    fetchBranches() {
      if (this.repository.id_) {
        RepositoryService.getRepositoryBranches(this.repository.id_, 10000000, 0)
          .then((response) => {
            for (const branch of response.data.data) {
              if (branch.branch_name === this.repository.branch_name) {
                this.selectedBranch = branch;
              }
              this.branchList.push(branch);
            }

            //Scan dates depend upon branch selected
            this.fetchScanDates();
          })
          .catch((error) => {
            AxiosConfig.handleError(error);
          });
      }
    },
  },
  watch: {
    repository: function (newVal, oldVal) {
      if (newVal !== oldVal) {
        this.fetchBranches();
      }
    },
  },
  components: {
    FindingStatusFilter,
    Multiselect,
    RuleFilter,
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
