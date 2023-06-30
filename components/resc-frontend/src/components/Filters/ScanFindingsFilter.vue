<template>
  <div>
    <div class="row">
      <!-- Scan Date Filter -->
      <div class="col-md-3 ml-3">
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
        <RuleFilter
          ref="ruleFilterChildComponent"
          :options="ruleList"
          @on-rule-change="handleRuleFilterChange"
        />
      </div>

      <!-- Status Filter -->
      <div class="col-md-3">
        <FindingStatusFilter @on-findings-status-change="onStatusFilterChange" />
      </div>

      <!-- Rule Tags Filter -->
      <div class="col-md-2">
        <RuleTagsFilter
          ref="ruleTagsFilterChildComponent"
          :options="ruleTagsList"
          :requestedRuleTagsFilterValue="selectedRuleTags"
          @on-rule-tags-change="handleRuleTagsFilterChange"
        />
      </div>
    </div>

    <!-- Include previous scan findings -->
    <div class="row">
      <div class="col-md-2 ml-3 pt-3">
        <b-form-checkbox
          v-model="includePreviousScans"
          name="check-button"
          switch
          @change="togglePreviousScans"
          @click.native="handleToggleButtonClick"
        >
          <small class="text-nowrap">Include previous scan findings</small>
        </b-form-checkbox>
      </div>
      <div class="col-md-1"></div>
    </div>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import Config from '@/configuration/config';
import DateUtils from '@/utils/date-utils';
import FindingStatusFilter from '@/components/Filters/FindingStatusFilter.vue';
import Multiselect from 'vue-multiselect';
import RuleFilter from '@/components/Filters/RuleFilter.vue';
import RulePackService from '@/services/rule-pack-service';
import RuleTagsFilter from '@/components/Filters/RuleTagsFilter.vue';
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
      ruleTagsList: [],
      statusList: [],
      selectedScan: null,
      selectedRule: null,
      selectedRuleTags: null,
      selectedStatus: null,
      includePreviousScans: false,
      skipRecords: Number(`${Config.value('skipRecords')}`),
      limitRecords: Number(`${Config.value('limitRecords')}`),
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
    handleToggleButtonClick() {
      this.refreshRuleTagsOnToggleOfPreviousScansButton();
    },
    togglePreviousScans() {
      if (this.includePreviousScans) {
        this.previousScans = [];
        this.getPreviousScans();
        this.$emit('previous-scans-checked', true);
        this.$emit(
          'include-previous-scans',
          this.selectedRule,
          this.selectedRuleTags,
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
    handleScanDateFilterChange() {
      // On scan date reset the Rule tags filter selection
      this.selectedRuleTags = null;
      this.$refs.ruleTagsFilterChildComponent.resetRuleTagsFilterSelection();

      // On scan date reset the Rule filter selection
      this.selectedRule = null;
      this.$refs.ruleFilterChildComponent.resetRuleFilterSelection();
      this.fetchRules();
    },
    handleRuleFilterChange(rule) {
      this.selectedRule = rule;
      this.handleFilterChange();
    },
    handleRuleTagsFilterChange(ruleTags) {
      this.selectedRuleTags = ruleTags;
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
          this.selectedStatus,
          this.selectedRuleTags
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
    getSelectedRulePacks() {
      const rulePacksForPreviousScanIds = [];
      for (const scan of this.previousScans) {
        rulePacksForPreviousScanIds.push(scan.rule_pack);
      }
      const rulePacks = this.includePreviousScans
        ? rulePacksForPreviousScanIds
        : [this.selectedScan.rulePackVersion];
      return rulePacks;
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

            // Fetch Rule Tags
            this.fetchRuleTags();
          })
          .catch((error) => {
            AxiosConfig.handleError(error);
          });
      }
    },
    fetchRuleTags() {
      const rulePackVersions = this.getSelectedRulePacks();
      RulePackService.getRuleTagsByRulePackVersions(rulePackVersions)
        .then((response) => {
          this.selectedRuleTags = null;
          this.ruleTagsList = response.data;

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
    },
    refreshRuleTagsOnToggleOfPreviousScansButton() {
      const rulePackVersions = this.getSelectedRulePacks();
      RulePackService.getRuleTagsByRulePackVersions(rulePackVersions)
        .then((response) => {
          this.ruleTagsList = response.data;
          this.selectedRuleTags = null;
          this.$refs.ruleTagsFilterChildComponent.resetRuleTagsFilterSelection();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchScanDates() {
      if (this.repository.id_) {
        ScanFindingsService.getScansByRepositoryId(
          this.repository.id_,
          this.skipRecords,
          this.limitRecords
        )
          .then((res) => {
            const response = res.data;
            this.scanDateList = [];

            this.scanList = response.sort(function (a, b) {
              return new Date(b.timestamp) - new Date(a.timestamp);
            });

            for (const scan of response) {
              const scanJson = {};
              scanJson['scanId'] = scan.id_;
              scanJson['scanDate'] = DateUtils.formatDate(scan.timestamp);
              scanJson['scanType'] = scan.scan_type === 'INCREMENTAL' ? 'Incremental' : 'Base';
              scanJson['rulePackVersion'] = scan.rule_pack;

              // Set scan date value in select option when user clicks a record from Repositories page
              if (this.$route.params.scanId == scan.id_) {
                this.selectedScan = scanJson;
              }
              this.scanDateList.push(scanJson);
            }

            //Sort scan dates
            this.scanDateList.sort(DateUtils.sortListByDate);

            //Rules depend upon scan/scan date selected
            this.fetchRules();
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
        this.fetchScanDates();
      }
    },
  },
  components: {
    FindingStatusFilter,
    Multiselect,
    RuleFilter,
    RuleTagsFilter,
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
