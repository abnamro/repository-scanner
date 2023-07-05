<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">REPOSITORIES</small></h3>
    </div>

    <!-- Spinner -->
    <Spinner :active="spinnerActive" />

    <!--Repository Filters -->
    <div class="ml-3 mt-4">
      <RepositoriesPageFilter
        :projectOptions="projectNames"
        :repositoryOptions="repositoryNames"
        @on-filter-change="handleFilterChange"
      ></RepositoriesPageFilter>
    </div>

    <!--Repository Table -->
    <div v-if="!hasRecords" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <div class="p-3" v-if="hasRecords">
      <b-table
        id="repositories-table"
        sticky-header="85vh"
        :items="repositoryList"
        :fields="fields"
        :current-page="currentPage"
        :per-page="0"
        primary-key="id_"
        v-model="currentItems"
        responsive
        small
        head-variant="light"
        :tbody-tr-class="rowClass"
        @row-clicked="goToScanFindings"
      >
        <!-- Repository Column -->
        <template #cell(repository_name)="data">
          {{ data.item.repository_name | truncate(25, '...') }}
        </template>

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
      ></Pagination>
    </div>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import Config from '@/configuration/config';
import CommonUtils from '@/utils/common-utils';
import DateUtils from '@/utils/date-utils';
import HealthBar from '@/components/Common/HealthBar.vue';
import Pagination from '@/components/Common/Pagination.vue';
import RepositoryService from '@/services/repository-service';
import RepositoriesPageFilter from '@/components/Filters/RepositoriesPageFilter.vue';
import Spinner from '@/components/Common/Spinner.vue';
import spinnerMixin from '@/mixins/spinner.js';

export default {
  name: 'Repositories',
  mixins: [spinnerMixin],
  data() {
    return {
      repositoryList: [],
      currentItems: [],
      totalRows: 0,
      currentPage: 1,
      perPage: Number(`${Config.value('defaultPageSize')}`),
      pageSizes: [20, 50, 100],
      requestedPageNumber: 1,
      vcsFilter: null,
      repositoryFilter: '',
      projectFilter: '',
      projectNames: [],
      repositoryNames: [],
      includeZeroFindingRepos: false,
      fields: [
        {
          key: 'project_key',
          sortable: true,
          label: 'Project',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '10%' },
        },
        {
          key: 'repository_name',
          sortable: true,
          label: 'Repository',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '20%' },
        },
        {
          key: 'vcs_provider',
          sortable: true,
          label: 'VCS Provider',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '10%' },
          formatter: 'formatVcsProvider',
        },
        {
          key: 'last_scan_timestamp',
          sortable: true,
          label: 'Last Scan Date',
          class: 'text-left',
          thStyle: { borderTop: '0px', width: '20%' },
          formatter: 'formatDate',
        },
        {
          key: 'total_findings_count',
          sortable: true,
          label: 'Findings Count',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '15%' },
        },
        {
          key: 'findings',
          label: 'Findings(%)',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '25%' },
        },
      ],
    };
  },
  computed: {
    hasRecords() {
      return this.repositoryList.length > 0;
    },
    skipRowCount() {
      return (this.currentPage - 1) * this.perPage;
    },
  },
  methods: {
    rowClass(item) {
      return item.last_scan_id ? 'row-clickable' : 'row-unclickable';
    },
    formatDate(timestamp) {
      const date = DateUtils.formatDate(timestamp);
      return timestamp ? date : 'Not Scanned';
    },
    formatVcsProvider(vcsProvider) {
      return CommonUtils.formatVcsProvider(vcsProvider);
    },
    handlePageClick(page) {
      this.currentPage = page;
      this.fetchPaginatedRepositories();
    },
    handlePageSizeChange(pageSize) {
      this.perPage = Number(pageSize);
      this.currentPage = 1;
      this.fetchPaginatedRepositories();
    },
    goToScanFindings(record) {
      if (record.last_scan_id) {
        const routeData = this.$router.resolve({
          name: 'ScanFindings',
          params: { scanId: record.last_scan_id },
        });
        window.open(routeData.href, '_blank');
      }
    },
    handleFilterChange(vcsProvider, project, repository, includeZeroFindingRepos) {
      this.vcsFilter = vcsProvider;
      this.projectFilter = project;
      this.repositoryFilter = repository;
      this.includeZeroFindingRepos = includeZeroFindingRepos;
      this.currentPage = 1;
      this.fetchDistinctProjects();
      this.fetchDistinctRepositories();
      this.fetchPaginatedRepositories();
    },
    fetchPaginatedRepositories() {
      this.repositoryList = [];
      this.showSpinner();
      RepositoryService.getRepositoriesWithFindingsMetadata(
        this.perPage,
        this.skipRowCount,
        this.vcsFilter,
        this.projectFilter,
        this.repositoryFilter,
        this.includeZeroFindingRepos
      )
        .then((response) => {
          this.totalRows = response.data.total;
          this.repositoryList = response.data.data;
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    fetchDistinctProjects() {
      RepositoryService.getDistinctProjects(
        this.vcsFilter,
        this.repositoryFilter,
        this.includeZeroFindingRepos
      )
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
      RepositoryService.getDistinctRepositories(
        this.vcsFilter,
        this.projectFilter,
        this.includeZeroFindingRepos
      )
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
    this.fetchDistinctProjects();
    this.fetchDistinctRepositories();
    this.fetchPaginatedRepositories();
  },
  components: {
    HealthBar,
    Pagination,
    RepositoriesPageFilter,
    Spinner,
  },
};
</script>
