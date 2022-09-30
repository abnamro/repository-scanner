<template>
  <b-card no-body class="text-left card-color">
    <!-- Spinner -->
    <Spinner :active="spinnerActive" />

    <!--Branch Findings Table -->
    <div v-if="!hasRecords" class="text-center cursor-defaultclear">
      <br />
      <br />No Record Found...
    </div>

    <div class="p-3" v-if="hasRecords">
      <b-table
        sticky-header="85vh"
        :items="branchList"
        :fields="fields"
        :current-page="currentPage"
        :per-page="0"
        primary-key="id_"
        v-model="currentItems"
        responsive
        head-variant="light"
        @row-clicked="goToFindings"
      >
        <!-- Health Bar Column -->
        <template #cell(findings)="data">
          <HealthBar
            :truePositive="data.item.true_positive"
            :falsePositive="data.item.false_positive"
            :notAnalyzed="data.item.not_analyzed"
            :underReview="data.item.under_review"
            :clarificationRequired="data.item.clarification_required"
            :totalCount="data.item.total_findings_count"
          />
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
        v-if="needsPagination"
      ></Pagination>
    </div>
  </b-card>
</template>

<script>
import BranchService from '@/services/branch-service';
import Config from '@/configuration/config';
import DateUtils from '@/utils/date-utils';
import HealthBar from '@/components/Common/HealthBar.vue';
import Pagination from '@/components/Common/Pagination.vue';
import PushNotification from '@/utils/push-notification';
import RepositoryService from '@/services/repository-service';
import Spinner from '@/components/Common/Spinner.vue';
import spinnerMixin from '@/mixins/spinner.js';

export default {
  name: 'RepositoryBranchesPanel',
  mixins: [spinnerMixin],
  props: {
    repositoryInfo: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      branchList: [],
      currentItems: [],
      totalRows: 0,
      currentPage: 1,
      perPage: `${Config.value('defaultPageSize')}`,
      pageSizes: [20, 50, 100],
      requestedPageNumber: 1,

      fields: [
        {
          key: 'branch_name',
          sortable: true,
          label: 'Branch',
          class: 'text-left',
          thStyle: { borderTop: '0px', width: '20%' },
        },
        {
          key: 'last_scan_datetime',
          sortable: true,
          label: 'Last Scan',
          class: 'text-left',
          thStyle: { borderTop: '0px', width: '20%' },
          formatter: 'formatDate',
        },
        {
          key: 'last_scan_finding_count',
          sortable: true,
          label: 'Last Run Count',
          class: 'text-left',
          thStyle: { borderTop: '0px', width: '15%' },
          formatter: 'formatCount',
        },
        {
          key: 'scan_finding_count',
          sortable: true,
          label: 'Total Count',
          class: 'text-left',
          thStyle: { borderTop: '0px', width: '15%' },
          formatter: 'formatCount',
        },
        {
          key: 'findings',
          label: 'Findings(%)',
          class: 'position-relative  text-left',
          thStyle: { borderTop: '0px', width: '30%' },
        },
      ],
    };
  },
  computed: {
    hasRecords() {
      return this.branchList.length > 0;
    },
    needsPagination() {
      return this.branchList.length > 0 && this.totalRows > this.perPage;
    },
    skipRowCount() {
      return (this.currentPage - 1) * this.perPage;
    },
  },
  methods: {
    formatDate(timestamp) {
      const date = DateUtils.formatDate(timestamp);
      return date === 'Jan 01, 1' ? 'Not Scanned' : date;
    },
    formatCount(count) {
      return count === -1 ? 'Not Available' : count;
    },
    handlePageClick(page) {
      this.currentPage = page;
      this.fetchPaginatedBranches();
    },
    handlePageSizeChange(pageSize) {
      this.perPage = Number(pageSize);
      this.currentPage = 1;
      this.fetchPaginatedBranches();
    },
    goToFindings(record) {
      const routeData = this.$router.resolve({
        name: 'ScanFindings',
        params: { scanId: record.last_scan_id },
      });
      window.open(routeData.href, '_blank');
    },
    fetchPaginatedBranches() {
      this.showSpinner();
      RepositoryService.getRepositoryBranches(
        this.repositoryInfo.id_,
        this.perPage,
        this.skipRowCount
      )
        .then((response) => {
          this.totalRows = response.data.total;
          //Add healthbar data
          for (const branch of response.data.data) {
            BranchService.getFindingsCountByStatusForBranch(branch.id_)
              .then((res) => {
                branch.true_positive = res.data.true_positive;
                branch.false_positive = res.data.false_positive;
                branch.not_analyzed = res.data.not_analyzed;
                branch.under_review = res.data.under_review;
                branch.clarification_required = res.data.clarification_required;
                branch.total_findings_count = res.data.total_findings_count;
                this.branchList.push(branch);
              })
              .catch((error) => {
                PushNotification.danger(error.message, 'Error', 5000);
              });
          }
          this.hideSpinner();
        })
        .catch((error) => {
          PushNotification.danger(error.message, 'Error', 5000);
        });
    },
  },
  created() {
    this.fetchPaginatedBranches();
  },
  components: { HealthBar, Pagination, Spinner },
};
</script>
