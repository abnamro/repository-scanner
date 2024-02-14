<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-start page-title">
      <h3><small class="text-nowrap">REPOSITORIES</small></h3>
    </div>

    <SpinnerVue v-if="!loadedData" />

    <!--Repository Filters -->
    <div class="ml-3 mt-4">
      <RepositoriesPageFilter
        v-model:projectOptions="projectNames"
        v-model:repositoryOptions="repositoryNames"
        @on-filter-change="handleFilterChange"
      ></RepositoriesPageFilter>
    </div>

    <!--Repository Table -->
    <div v-if="!hasRecords && loadedData" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <div class="p-3" v-if="hasRecords">
      <!-- sticky-header="85vh" is not supported yet. -->
      <b-table
        id="repositories-table"
        :sticky-header="true"
        :items="repositoryList"
        :fields="fields"
        :current-page="1"
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
          {{ truncate((data.item as RepositoryEnrichedRead).repository_name, 25, '...') }}
        </template>

        <!-- Health Bar Column -->
        <template #cell(findings)="data">
          <HealthBar
            :truePositive="(data.item as RepositoryEnrichedRead).true_positive"
            :falsePositive="(data.item as RepositoryEnrichedRead).false_positive"
            :notAnalyzed="(data.item as RepositoryEnrichedRead).not_analyzed"
            :underReview="(data.item as RepositoryEnrichedRead).under_review"
            :clarificationRequired="(data.item as RepositoryEnrichedRead).clarification_required"
            :totalCount="(data.item as RepositoryEnrichedRead).total_findings_count"
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

<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import Config from '@/configuration/config';
import CommonUtils from '@/utils/common-utils';
import DateUtils from '@/utils/date-utils';
import HealthBar from '@/components/Common/HealthBar.vue';
import Pagination from '@/components/Common/PaginationVue.vue';
import RepositoryService from '@/services/repository-service';
import RepositoriesPageFilter from '@/components/Filters/RepositoriesPageFilter.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import type { RepositoryEnrichedRead, VCSProviders } from '@/services/shema-to-types';
import type { TableItem } from 'bootstrap-vue-next';

const loadedData = ref(false);
const router = useRouter();

const repositoryList = ref([] as RepositoryEnrichedRead[]);
const currentItems = ref([] as RepositoryEnrichedRead[]);
const totalRows = ref(0);
const currentPage = ref(1);
const perPage = ref(Number(`${Config.value('defaultPageSize')}`));
const pageSizes = ref([20, 50, 100]);
const requestedPageNumber = ref(1);
const vcsFilter = ref([] as VCSProviders[]);
const repositoryFilter = ref(undefined as string | undefined);
const projectFilter = ref(undefined as string | undefined);
const projectNames = ref([] as string[]);
const repositoryNames = ref([] as string[]);
const includeZeroFindingRepos = ref(false);
const fields = ref([
  {
    key: 'project_key',
    sortable: true,
    label: 'Project',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px', width: '10%' },
  },
  {
    key: 'repository_name',
    sortable: true,
    label: 'Repository',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px', width: '20%' },
  },
  {
    key: 'vcs_provider',
    sortable: true,
    label: 'VCS Provider',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px', width: '10%' },
    formatter: 'formatVcsProvider',
  },
  {
    key: 'last_scan_timestamp',
    sortable: true,
    label: 'Last Scan Date',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px', width: '20%' },
    formatter: 'formatDate',
  },
  {
    key: 'total_findings_count',
    sortable: true,
    label: 'Findings Count',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px', width: '15%' },
  },
  {
    key: 'findings',
    label: 'Findings(%)',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px', width: '25%' },
  },
]);

const hasRecords = computed(() => {
  return repositoryList.value.length > 0;
});

const skipRowCount = computed(() => {
  return (currentPage.value - 1) * perPage.value;
});

// remove me later
function truncate(text: string, length: number, suffix: string) {
  if (text.length > length) {
    return text.substring(0, length) + suffix;
  } else {
    return text;
  }
}

function rowClass(item: RepositoryEnrichedRead) {
  return item.last_scan_id ? 'row-clickable' : 'row-unclickable';
}

// It is used in formatting above.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function formatDate(timestamp: number) {
  const date = DateUtils.formatDate(timestamp);
  return timestamp ? date : 'Not Scanned';
}

// It is used in formatting above.
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function formatVcsProvider(vcsProvider: VCSProviders) {
  return CommonUtils.formatVcsProvider(vcsProvider);
}

function handlePageClick(page: number) {
  currentPage.value = page;
  fetchPaginatedRepositories();
}

function handlePageSizeChange(pageSize: number) {
  perPage.value = Number(pageSize);
  currentPage.value = 1;
  fetchPaginatedRepositories();
}

function goToScanFindings(record: TableItem) {
  // Casting back to RepositoryEnrichedRead
  const recordItem = record as RepositoryEnrichedRead;
  if (recordItem.last_scan_id) {
    const routeData = router.resolve({
      name: 'ScanFindings',
      params: { scanId: recordItem.last_scan_id },
    });
    window.open(routeData.href, '_blank');
  }
}

function handleFilterChange(
  vcsProvider: VCSProviders[],
  project: string | undefined,
  repository: string | undefined,
  includeZeroFindingReposArg: boolean,
) {
  vcsFilter.value = vcsProvider;
  projectFilter.value = project;
  repositoryFilter.value = repository;
  includeZeroFindingRepos.value = includeZeroFindingReposArg;
  currentPage.value = 1;
  fetchDistinctProjects();
  fetchDistinctRepositories();
  fetchPaginatedRepositories();
}

function fetchPaginatedRepositories() {
  repositoryList.value = [];
  loadedData.value = false;
  RepositoryService.getRepositoriesWithFindingsMetadata(
    perPage.value,
    skipRowCount.value,
    vcsFilter.value,
    projectFilter.value,
    repositoryFilter.value,
    includeZeroFindingRepos.value,
  )
    .then((response) => {
      totalRows.value = response.data.total;
      repositoryList.value = response.data.data;
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function fetchDistinctProjects() {
  RepositoryService.getDistinctProjects(
    vcsFilter.value,
    repositoryFilter.value,
    includeZeroFindingRepos.value,
  )
    .then((response) => {
      projectNames.value = [];
      for (const projectKey of response.data) {
        projectNames.value.push(projectKey);
      }
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}
function fetchDistinctRepositories() {
  RepositoryService.getDistinctRepositories(
    vcsFilter.value,
    projectFilter.value,
    includeZeroFindingRepos.value,
  )
    .then((response) => {
      repositoryNames.value = [];
      for (const repoName of response.data) {
        repositoryNames.value.push(repoName);
      }
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

onMounted(() => {
  fetchDistinctProjects();
  fetchDistinctRepositories();
  fetchPaginatedRepositories();
});
</script>
