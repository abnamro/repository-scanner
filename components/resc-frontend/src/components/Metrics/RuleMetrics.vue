<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">RULE METRICS</small></h3>
    </div>

    <!-- Spinner -->
    <Spinner :active="spinnerActive" />

    <div class="mt-4">
      <div class="col-md-4">
        <RulePackFilter
          :selectedRulePackVersionsList="selectedRulePackVersionsList"
          :rulePackVersions="allRulePackVersions"
          @on-rule-pack-version-change="onRulePackVersionChange"
        />
      </div>
    </div>

    <!--Rule Metrics Table -->
    <div v-if="!hasRecords" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <div class="p-3" v-if="hasRecords">
      <b-table
        id="rule-metrics-table"
        sticky-header="85vh"
        :no-border-collapse="true"
        :items="ruleList"
        :fields="fields"
        primary-key="rule_name"
        responsive
        small
        head-variant="light"
        @row-clicked="goToRuleAnalysisPage"
      >
        <!-- True Positive Rate Column -->
        <template #cell(true_positive_rate)="data">
          {{ calculateTruePositiveRate(data) }}
        </template>

        <!-- True Positive Count Column -->
        <template #cell(true_positive)="data">
          <span v-for="(item, i) in data.item.finding_statuses_count" :key="i">
            <span v-if="item.status == 'TRUE_POSITIVE'">
              {{ item.count }}
            </span>
          </span>
        </template>

        <!-- False Positive Count Column -->
        <template #cell(false_positive)="data">
          <span v-for="(item, i) in data.item.finding_statuses_count" :key="i">
            <span v-if="item.status == 'FALSE_POSITIVE'">
              {{ item.count }}
            </span>
          </span>
        </template>

        <!-- Clarification Required Count Column -->
        <template #cell(clarification_required)="data">
          <span v-for="(item, i) in data.item.finding_statuses_count" :key="i">
            <span v-if="item.status == 'CLARIFICATION_REQUIRED'">
              {{ item.count }}
            </span>
          </span>
        </template>

        <!-- Under Review Count Column -->
        <template #cell(under_review)="data">
          <span v-for="(item, i) in data.item.finding_statuses_count" :key="i">
            <span v-if="item.status == 'UNDER_REVIEW'">
              {{ item.count }}
            </span>
          </span>
        </template>

        <!-- Under Review Count Column -->
        <template #cell(not_analyzed)="data">
          <span v-for="(item, i) in data.item.finding_statuses_count" :key="i">
            <span v-if="item.status == 'NOT_ANALYZED'">
              {{ item.count }}
            </span>
          </span>
        </template>

        <!-- Health Bar Column -->
        <template #cell(health)="data">
          <span v-for="(item, i) in data.item.finding_statuses_count" :key="i">
            <span v-if="item.status == 'TRUE_POSITIVE'" :set="(tpCount = item.count)"></span>
            <span v-if="item.status == 'FALSE_POSITIVE'" :set="(fpCount = item.count)"></span>
            <span
              v-if="item.status == 'CLARIFICATION_REQUIRED'"
              :set="(crCount = item.count)"
            ></span>
            <span v-if="item.status == 'UNDER_REVIEW'" :set="(urCount = item.count)"></span>
            <span v-if="item.status == 'NOT_ANALYZED'" :set="(naCount = item.count)"></span>
          </span>
          <HealthBar
            :truePositive="tpCount"
            :falsePositive="fpCount"
            :notAnalyzed="naCount"
            :underReview="urCount"
            :clarificationRequired="crCount"
            :totalCount="data.item.finding_count"
          />
        </template>

        <!-- Total Calculation Row-->
        <template slot="bottom-row">
          <td :class="ruleTotalRowClass">Sum</td>
          <td :class="ruleTotalRowClass">Avg:{{ avgTruePosiitveRate }}%</td>
          <td :class="ruleTotalRowClass">{{ truePositiveTotalCount }}</td>
          <td :class="ruleTotalRowClass">{{ falsePositiveTotalCount }}</td>
          <td :class="ruleTotalRowClass">{{ clarificationRequiredTotalCount }}</td>
          <td :class="ruleTotalRowClass">{{ underReviewTotalCount }}</td>
          <td :class="ruleTotalRowClass">{{ notAnalyzedTotalCount }}</td>
          <td :class="ruleTotalRowClass">{{ totalFindingsCountForAllRules }}</td>
          <td :class="ruleTotalRowClass"></td>
        </template>
      </b-table>
    </div>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import HealthBar from '@/components/Common/HealthBar.vue';
import RulePackFilter from '@/components/Filters/RulePackFilter.vue';
import RulePackService from '@/services/rule-pack-service';
import RuleService from '@/services/rule-service';
import Spinner from '@/components/Common/Spinner.vue';
import spinnerMixin from '@/mixins/spinner.js';
import Store from '@/store/index.js';

export default {
  name: 'RuleMetrics',
  mixins: [spinnerMixin],
  props: {
    selectedRulePackVersionsList: {
      type: Array,
      required: false,
      default: () => [],
    },
    rulePackVersions: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  data() {
    return {
      ruleList: [],
      truePositiveTotalCount: 0,
      falsePositiveTotalCount: 0,
      clarificationRequiredTotalCount: 0,
      underReviewTotalCount: 0,
      notAnalyzedTotalCount: 0,
      totalFindingsCountForAllRules: 0,
      truePositiveRateList: [],
      avgTruePosiitveRate: 0,
      allRulePackVersions: [],
      selectedRulePackVersions: [],
      ruleTotalRowClass: ['text-left', 'font-weight-bold'],
      fields: [
        {
          key: 'rule_name',
          sortable: true,
          label: 'Rule',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'true_positive_rate',
          sortable: false,
          label: 'True Positive Rate',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'true_positive',
          sortable: false,
          label: 'True Positive',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'false_positive',
          sortable: false,
          label: 'False Positive',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'clarification_required',
          sortable: false,
          label: 'Clarification Required',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'under_review',
          sortable: false,
          label: 'Under Review',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'not_analyzed',
          sortable: false,
          label: 'Not Analyzed',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'finding_count',
          sortable: true,
          label: 'Total Count',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
          tdClass: 'font-weight-bold',
        },
        {
          key: 'health',
          label: 'Findings(%)',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '25%' },
        },
      ],
    };
  },
  computed: {
    hasRecords() {
      return this.ruleList.length > 0;
    },
  },
  methods: {
    fetchRulePackVersions() {
      RulePackService.getRulePackVersions(10000, 0)
        .then((response) => {
          this.allRulePackVersions = [];
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
            this.allRulePackVersions.push(rulePackJson);
          }
          this.fetchRulesWithFindingStatusCount();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchRulesWithFindingStatusCount() {
      this.showSpinner();
      RuleService.getRulesWithFindingStatusCount(this.selectedRulePackVersions)
        .then((response) => {
          this.ruleList = response.data;
          this.getTotalCountRowValuesForRuleMetricsTable();
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    calculateTruePositiveRate(data) {
      let true_positive_count = 0;
      let false_positive_count = 0;
      data.item.finding_statuses_count.forEach((finding_status) => {
        if (finding_status.status === 'TRUE_POSITIVE') {
          true_positive_count = finding_status.count;
        }
        if (finding_status.status === 'FALSE_POSITIVE') {
          false_positive_count = finding_status.count;
        }
      });
      let true_positive_rate = Math.round(
        (true_positive_count / (true_positive_count + false_positive_count)) * 100
      );
      true_positive_rate = true_positive_rate || 0;
      return `${true_positive_rate}%`;
    },
    getTotalCountRowValuesForRuleMetricsTable() {
      this.ruleList.forEach((rule) => {
        let tpCount = 0;
        let fpCount = 0;
        let true_positive_rate = 0;
        this.totalFindingsCountForAllRules += rule.finding_count;
        rule.finding_statuses_count.forEach((finding_status) => {
          if (finding_status.status === 'TRUE_POSITIVE') {
            this.truePositiveTotalCount += finding_status.count;
            tpCount = finding_status.count;
          }
          if (finding_status.status === 'FALSE_POSITIVE') {
            this.falsePositiveTotalCount += finding_status.count;
            fpCount = finding_status.count;
          }
          if (finding_status.status === 'CLARIFICATION_REQUIRED') {
            this.clarificationRequiredTotalCount += finding_status.count;
          }
          if (finding_status.status === 'UNDER_REVIEW') {
            this.underReviewTotalCount += finding_status.count;
          }
          if (finding_status.status === 'NOT_ANALYZED') {
            this.notAnalyzedTotalCount += finding_status.count;
          }
        });

        true_positive_rate = Math.round((tpCount / (tpCount + fpCount)) * 100);
        true_positive_rate = true_positive_rate || 0;
        this.truePositiveRateList.push(true_positive_rate);
      });

      this.calculateAverageTruePositiveRatePercentage();
    },
    calculateAverageTruePositiveRatePercentage() {
      if (this.ruleList.length > 0 && this.truePositiveRateList.length > 0) {
        const sum_of_true_positve_rates = this.truePositiveRateList.reduce((a, b) => a + b, 0);
        this.avgTruePosiitveRate = `${Math.round(
          sum_of_true_positve_rates / this.ruleList.length
        )}`;
      }
    },
    goToRuleAnalysisPage(record) {
      Store.commit('update_previous_route_state', {
        ruleName: record.rule_name,
      });
      this.$router.push({ name: 'RuleAnalysis' });
    },
    onRulePackVersionChange(rulePackVersions) {
      this.selectedRulePackVersions = rulePackVersions;
      this.fetchRulesWithFindingStatusCount();
    },
  },
  created() {
    this.fetchRulePackVersions();
  },
  components: {
    HealthBar,
    RulePackFilter,
    Spinner,
  },
};
</script>
