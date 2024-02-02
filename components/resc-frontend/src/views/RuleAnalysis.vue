<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-start page-title">
      <h3><small class="text-nowrap">RULE ANALYSIS</small></h3>
    </div>

    <SpinnerVue v-if="!loadedData" />

    <!-- Filters -->
    <div class="mt-4">
      <RuleAnalysisFilter
        :projectOptions="projectNames"
        :repositoryOptions="repositoryNames"
        :rulePackPreSelected="selectedRulePackVersionsList"
        :rulePackOptions="rulePackVersions"
        @on-filter-change="handleFilterChange"
      ></RuleAnalysisFilter>
    </div>

    <div class="ml-3">
      <!-- Button to audit multiple findings -->
      <b-button
        class="float-left mt-2 mb-2"
        variant="primary"
        size="sm"
        v-on:click="showAuditModal()"
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
    <div v-if="!hasRecords && loadedData" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <!-- sticky-header="85vh" -->
    <div class="p-3" v-if="hasRecords">
      <b-table
        id="rule-analysis-table"
        :sticky-header="true"
        :items="findingList"
        :fields="fields"
        :current-page="1"
        :per-page="0"
        primary-key="id_"
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
            :value="(data.item as DetailedFindingRead).id_"
            @change="selectSingleCheckbox"
          ></b-form-checkbox>
        </template>

        <!-- Collapse Icon Column -->
        <template v-slot:cell(toggle_row)="{ detailsShowing }">
          <FontAwesomeIcon
            size="lg"
            class="collapse-arrow"
            name="dropdown-icon"
            icon="angle-right"
            :rotation="detailsShowing ? 90 : undefined"
          />
        </template>

        <!-- Path Column -->
        <template #cell(file_path)="data">
          {{ truncate((data.item as DetailedFindingRead).file_path, 45, '...') }}
        </template>

        <!-- Line Column -->
        <template #cell(line_number)="data">
          {{ (data.item as DetailedFindingRead).line_number }}
        </template>

        <!-- Position Column -->
        <template #cell(position)="data">
          {{ (data.item as DetailedFindingRead).column_start }} -
          {{ (data.item as DetailedFindingRead).column_end }}
        </template>

        <!-- Status Column -->
        <template #cell(status)="data">
          <FindingStatusBadge
            :status="(data.item as DetailedFindingRead).status ?? 'NOT_ANALYZED'"
          />
        </template>

        <!-- Remaining Columns (Rule) -->
        <template #cell()="data">
          {{ data.value }}
        </template>

        <!-- Expand Table Row To Display Finding Panel -->
        <template v-slot:row-details="{ item }">
          <FindingPanel
            :finding="(item as DetailedFindingRead)"
            :repository="{
              project_key: item.project_key,
              repository_name: item.repository_name,
              repository_url: item.repository_url,
              vcs_provider: item.vcs_provider,
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

<script lang="ts" setup>
import AuditModal from '@/components/ScanFindings/AuditModal.vue';
import Config from '@/configuration/config';
import AxiosConfig from '@/configuration/axios-config';
import FindingPanel from '@/components/ScanFindings/FindingPanel.vue';
import FindingsService, { type QueryFilterType } from '@/services/findings-service';
import FindingStatusBadge from '@/components/Common/FindingStatusBadge.vue';
import RepositoryService from '@/services/repository-service';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import Pagination from '@/components/Common/PaginationVue.vue';
import { type RuleAnalysisFilter } from '@/components/Filters/RuleAnalysisFilter.vue';
import RulePackService from '@/services/rule-pack-service';
import { useAuthUserStore, type PreviousRouteState } from '@/store/index';
import { computed, nextTick, onMounted, ref, type Ref } from 'vue';
import type {
  DetailedFindingRead,
  FindingStatus,
  PaginationType,
  RulePackRead,
  VCSProviders,
} from '@/services/shema-to-types';
import type { AxiosResponse } from 'axios';
import type { TableItem } from 'bootstrap-vue-next';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

type TableItemDetailedFindingRead = DetailedFindingRead & TableItem;

const loadedData = ref(false);
const auditModal = ref();

const findingList = ref([] as TableItemDetailedFindingRead[]);
const totalRows = ref(0);
const currentPage = ref(1);
const perPage = ref(Number(`${Config.value('defaultPageSize')}`));
const pageSizes = ref([20, 50, 100]);
const requestedPageNumber = ref(1);
const rulePackVersions = ref([] as RulePackRead[]);
const ruleTagsList = ref([] as string[]);
const projectNames = ref([] as string[]);
const repositoryNames = ref([] as string[]);
const selectedStartDate = ref(undefined) as Ref<string | undefined>;
const selectedEndDate = ref(undefined) as Ref<string | undefined>;
const selectedVcsProvider = ref([] as VCSProviders[]);
const selectedStatus = ref(undefined) as Ref<FindingStatus[] | undefined>;
const selectedProject = ref(undefined) as Ref<string | undefined>;
const selectedRepository = ref(undefined) as Ref<string | undefined>;
const selectedRule = ref(undefined) as Ref<string[] | undefined>;
const selectedRuleTags = ref(undefined) as Ref<string[] | undefined>;
const selectedRulePackVersions = ref([] as string[]);
const selectedRulePackVersionsList = ref([] as RulePackRead[]);
const selectedCheckBoxIds = ref([] as number[]);
const allSelected = ref(false);
const fields = ref([
  {
    key: 'select',
    label: '',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'toggle_row',
    label: '',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'project_key',
    sortable: true,
    label: 'Project',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'repository_name',
    sortable: true,
    label: 'Repository',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'rule_name',
    sortable: true,
    label: 'Rule',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'file_path',
    sortable: true,
    label: 'File Path',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'line_number',
    sortable: false,
    label: 'Line',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'position',
    sortable: true,
    label: 'Position',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'status',
    sortable: true,
    label: 'Status',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
]);

const hasRecords = computed(() => findingList.value.length > 0);
const skipRowCount = computed(() => (currentPage.value - 1) * perPage.value);
const auditButtonDisabled = computed(() => selectedCheckBoxIds.value.length <= 0);

function truncate(text: string, length: number, suffix: string) {
  if (text.length > length) {
    return text.substring(0, length) + suffix;
  } else {
    return text;
  }
}

function isRedirectedFromRuleMetricsPage() {
  const store = useAuthUserStore();
  const sourceRoute = store.sourceRoute;
  const destinationRoute = store.destinationRoute;
  return sourceRoute === '/metrics/rule-metrics' &&
    destinationRoute === '/rule-analysis' &&
    store.previousRouteState
    ? true
    : false;
}

function selectSingleCheckbox() {
  allSelected.value = false;
}

function selectAllCheckboxes() {
  selectedCheckBoxIds.value = [];
  if (allSelected.value) {
    for (const finding of findingList.value) {
      selectedCheckBoxIds.value.push(finding.id_);
    }
  }
}

function showAuditModal() {
  auditModal.value.show();
}

function handlePageClick(page: number) {
  allSelected.value = false;
  currentPage.value = page;
  fetchPaginatedDetailedFindings();
}

function handlePageSizeChange(pageSize: number) {
  perPage.value = pageSize;
  currentPage.value = 1;
  fetchPaginatedDetailedFindings();
}

function toggleFindingDetails(row: TableItem) {
  if (row._showDetails) {
    row._showDetails = false;
  } else {
    findingList.value.forEach((_item, idx, theArray) => {
      theArray[idx]._showDetails = false;
    });
    nextTick(() => {
      row._showDetails = true;
    });
  }
}
function fetchPaginatedDetailedFindings() {
  loadedData.value = false;
  const filterObj: QueryFilterType = {
    skip: skipRowCount.value,
    limit: perPage.value,
    startDate: selectedStartDate.value,
    endDate: selectedEndDate.value,
    vcsProvider: selectedVcsProvider.value,
    findingStatus: selectedStatus.value,
    project: selectedProject.value,
    repository: selectedRepository.value,
    rule: selectedRule.value,
    ruleTags: selectedRuleTags.value,
    rulePackVersions: selectedRulePackVersions.value,
  };

  findingList.value = [];

  FindingsService.getDetailedFindings(filterObj)
    .then((response: AxiosResponse<PaginationType<DetailedFindingRead>>) => {
      totalRows.value = 0;
      selectedCheckBoxIds.value = [];
      totalRows.value = response.data.total;
      findingList.value = response.data.data;
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function updateAudit(status: FindingStatus, comment: string) {
  findingList.value.forEach((finding: DetailedFindingRead, idx, theArray) => {
    if (selectedCheckBoxIds.value.includes(finding.id_)) {
      theArray[idx].status = status;
      theArray[idx].comment = comment;
    }
  });
  allSelected.value = false;
  fetchPaginatedDetailedFindings();
}

function handleFilterChange(filterObj: RuleAnalysisFilter) {
  selectedStartDate.value = filterObj.startDate;
  selectedEndDate.value = filterObj.endDate;
  selectedVcsProvider.value = filterObj.vcsProvider ?? [];
  selectedStatus.value = filterObj.status;
  selectedProject.value = filterObj.project;
  selectedRepository.value = filterObj.repository;
  selectedRule.value = filterObj.rule;
  selectedRuleTags.value = filterObj.ruleTags;
  selectedRulePackVersions.value = filterObj.rulePackVersions ?? [];
  currentPage.value = 1;
  allSelected.value = false;
  fetchDistinctProjects();
  fetchDistinctRepositories();
  fetchPaginatedDetailedFindings();
}

function fetchDistinctProjects() {
  RepositoryService.getDistinctProjects(selectedVcsProvider.value, selectedRepository.value)
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
  RepositoryService.getDistinctRepositories(selectedVcsProvider.value, selectedProject.value)
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

function fetchRulePackVersionsWhenRedirectedFromRuleMetricsPage() {
  const store = useAuthUserStore();
  RulePackService.getRulePackVersions(10000, 0)
    .then((response: AxiosResponse<PaginationType<RulePackRead>>) => {
      rulePackVersions.value = [];
      selectedRulePackVersions.value = [];
      response.data.data.forEach((rulePack) => {
        rulePackVersions.value.push(rulePack);
      });
      //Select rule pack versions passed from rule analysis scrren
      const previousRouteState = store.previousRouteState as PreviousRouteState;
      if (previousRouteState && previousRouteState.rulePackVersions !== undefined) {
        for (const obj of previousRouteState.rulePackVersions) {
          selectedRulePackVersions.value.push(obj.version);
          selectedRulePackVersionsList.value.push(obj);
        }
        fetchRuleTags();
        store.update_previous_route_state(null);
      }
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function fetchRulePackVersions() {
  RulePackService.getRulePackVersions(10000, 0)
    .then((response: AxiosResponse<PaginationType<RulePackRead>>) => {
      rulePackVersions.value = [];
      selectedRulePackVersions.value = [];
      selectedRulePackVersionsList.value = [];
      for (const index of response.data.data.keys()) {
        const data = response.data.data[index];
        if (data.active) {
          selectedRulePackVersions.value.push(data.version);
          selectedRulePackVersionsList.value.push(data);
        }
        rulePackVersions.value.push(data);
      }
      fetchPaginatedDetailedFindings();
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function fetchRuleTags() {
  RulePackService.getRuleTagsByRulePackVersions(selectedRulePackVersions.value)
    .then((response: AxiosResponse<string[]>) => {
      selectedRuleTags.value = [];
      ruleTagsList.value = response.data;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

onMounted(() => {
  if (isRedirectedFromRuleMetricsPage()) {
    fetchRulePackVersionsWhenRedirectedFromRuleMetricsPage();
  } else {
    const store = useAuthUserStore();
    store.update_previous_route_state(null);
    fetchRulePackVersions();
    fetchDistinctProjects();
    fetchDistinctRepositories();
  }
});
</script>
