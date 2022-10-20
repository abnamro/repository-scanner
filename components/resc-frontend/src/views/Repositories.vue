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
        head-variant="light"
        @row-clicked="toggleRepositoryDetails"
      >
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

        <!-- Expand Table Row To Display RepositoryBranches Panel -->
        <template v-slot:row-details="{ item }">
          <RepositoryBranchesPanel :repositoryInfo="item"></RepositoryBranchesPanel>
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
import HealthBar from '@/components/Common/HealthBar.vue';
import Pagination from '@/components/Common/Pagination.vue';
import RepositoryBranchesPanel from '@/components/RepositoryBranches/RepositoryBranchesPanel.vue';
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
      fields: [
        {
          key: 'toggle_row',
          label: '',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '5%' },
        },
        {
          key: 'project_key',
          sortable: true,
          label: 'Project',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '20%' },
        },
        {
          key: 'repository_name',
          sortable: true,
          label: 'Repository',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '25%' },
        },
        {
          key: 'vcs_provider',
          sortable: true,
          label: 'VCS Provider',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px', width: '10%' },
        },
        {
          key: 'total_findings_count',
          sortable: true,
          label: 'Total Count',
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
    handlePageClick(page) {
      this.currentPage = page;
      this.fetchPaginatedRepositories();
    },
    handlePageSizeChange(pageSize) {
      this.perPage = Number(pageSize);
      this.currentPage = 1;
      this.fetchPaginatedRepositories();
    },
    toggleRepositoryDetails(row) {
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
    handleFilterChange(vcsProvider, project, repository) {
      this.vcsFilter = vcsProvider;
      this.projectFilter = project;
      this.repositoryFilter = repository;
      this.currentPage = 1;
      this.fetchDistinctProjects();
      this.fetchDistinctRepositories();
      this.fetchPaginatedRepositories();
    },
    fetchPaginatedRepositories() {
      this.showSpinner();
      RepositoryService.getRepositoriesWithFindingsMetadata(
        this.perPage,
        this.skipRowCount,
        this.vcsFilter,
        this.projectFilter,
        this.repositoryFilter
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
      RepositoryService.getDistinctProjects(this.vcsFilter, this.repositoryFilter)
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
      RepositoryService.getDistinctRepositories(this.vcsFilter, this.projectFilter)
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
    RepositoryBranchesPanel,
    RepositoriesPageFilter,
    Spinner,
  },
};
</script>
