<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-start page-title">
      <h3><small class="text-nowrap">SCAN FINDINGS</small></h3>
    </div>

    <SpinnerVue v-if="!loadedData" />

    <!-- Repository Panel -->
    <div class="col-md-4 ml-3 mt-4 text-start">
      <RepositoryPanel :repository="repository" :vcs_instance="vcsInstance"></RepositoryPanel>
    </div>

    <div>
      <!-- Button to audit multiple findings -->
      <b-button
        class="float-left ml-3 audit-btn"
        variant="primary"
        size="sm"
        v-on:click="showAuditModal()"
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
    <div v-if="!hasRecords && loadedData" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <!-- sticky-header="85vh" -->
    <div class="p-3" v-if="hasRecords">
      <b-table
        id="scan-findings-table"
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
            :value="(data.item as AugmentedDetailedFindingRead).id_"
            @change="selectSingleCheckbox"
          >
          </b-form-checkbox>
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
          {{ truncate((data.item as AugmentedDetailedFindingRead).file_path, 45, '...') }}
        </template>

        <!-- Line Column -->
        <template #cell(line_number)="data">
          {{ (data.item as AugmentedDetailedFindingRead).line_number }}
        </template>

        <!-- Position Column -->
        <template #cell(position)="data">
          {{ (data.item as AugmentedDetailedFindingRead).column_start }} -
          {{ (data.item as AugmentedDetailedFindingRead).column_end }}
        </template>

        <!-- Status Column -->
        <template #cell(status)="data">
          <FindingStatusBadge
            :status="(data.item as AugmentedDetailedFindingRead).status ?? 'NOT_ANALYZED'"
          />
        </template>

        <!-- Remaining Columns (Rule) -->
        <template #cell()="data">
          {{ data.value }}
        </template>

        <!-- Scan Type Column -->
        <template #cell(scanType)="data">
          <ScanTypeBadge
            :scanType="((data.item as AugmentedDetailedFindingRead).scanType as string)"
            :incrementNumber="((data.item as AugmentedDetailedFindingRead).incrementNumber as number)"
          />
        </template>

        <!-- Expand Table Row To Display Finding Panel -->
        <template v-slot:row-details="{ item }">
          <FindingPanel
            :finding="(item as AugmentedDetailedFindingRead)"
            :repository="repository"
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

<script setup lang="ts">
import AuditModal from '@/components/ScanFindings/AuditModal.vue';
import AxiosConfig from '@/configuration/axios-config';
import Config from '@/configuration/config';
import FindingPanel from '@/components/ScanFindings/FindingPanel.vue';
import FindingStatusBadge from '@/components/Common/FindingStatusBadge.vue';
import Pagination from '@/components/Common/PaginationVue.vue';
import RepositoryPanel from '@/components/ScanFindings/RepositoryPanel.vue';
import ScanFindingsFilter from '@/components/Filters/ScanFindingsFilter.vue';
import ScanFindingsService from '@/services/scan-findings-service';
import ScanTypeBadge from '@/components/Common/ScanTypeBadge.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import FindingsService, { type QueryFilterType } from '@/services/findings-service';
import VCSInstanceService from '@/services/vcs-instance-service';
import { computed, nextTick, ref, type Ref } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import type {
  DetailedFindingRead,
  ScanRead,
  PaginationType,
  RepositoryRead,
  VCSInstanceRead,
  FindingStatus,
  AugmentedDetailedFindingRead,
} from '@/services/shema-to-types';
import type { AxiosResponse } from 'axios';
import type { TableItem } from 'bootstrap-vue-next';

const loadedData = ref(false);
const auditModal = ref();

type Props = {
  scanId: string;
};

type TableItemAugmentedDetailedFindingRead = AugmentedDetailedFindingRead & TableItem;

const props = defineProps<Props>();
const previousScanChecked = ref(false);
const scanType = ref(undefined) as Ref<string | undefined>;
const previousScanList = ref([] as ScanRead[]);
const incrementNumber = ref(undefined) as Ref<number | undefined>;
const repositoryId = ref(null) as Ref<number | null>;
const repository = ref({} as RepositoryRead);
const vcsInstance = ref({} as VCSInstanceRead);
const selectedCheckBoxIds = ref([] as number[]);
const allSelected = ref(false);
const findingList = ref([] as TableItemAugmentedDetailedFindingRead[]);
const selectedScanID = ref(Number(props.scanId));
const ruleFilter = ref([] as string[]);
const ruleTagsFilter = ref(undefined) as Ref<string[] | undefined>;
const statusFilter = ref(undefined) as Ref<FindingStatus[] | undefined>;
const totalRows = ref(0);
const currentPage = ref(1);
const perPage = ref(Number(`${Config.value('defaultPageSize')}`));
const pageSizes = ref([20, 50, 100]);
const requestedPageNumber = ref(1);
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
  {
    key: 'scanType',
    sortable: true,
    label: 'Scan Type',
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

function onPreviousScanChecked(checked: boolean) {
  previousScanChecked.value = checked;
}

function handlePageClick(page: number) {
  allSelected.value = false;
  currentPage.value = page;
  previousScanChecked.value ? fetchPreviousScanFindings() : fetchPaginatedFindingsByScanId();
}

function handlePageSizeChange(pageSize: number) {
  perPage.value = pageSize;
  currentPage.value = 1;
  previousScanChecked.value ? fetchPreviousScanFindings() : fetchPaginatedFindingsByScanId();
}

function toggleFindingDetails(row: TableItem) {
  if (row._showDetails) {
    row['_showDetails'] = false;
  } else {
    findingList.value.forEach((_item: TableItem, idx, theArray) => {
      theArray[idx]._showDetails = false;
    });
    nextTick(() => {
      row._showDetails = true;
    });
  }
}

function fetchVCSInstance() {
  VCSInstanceService.getVCSInstance(repository.value.vcs_instance)
    .then((res: AxiosResponse<VCSInstanceRead>) => {
      vcsInstance.value = res.data;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function fetchRepository() {
  if (repositoryId.value === null) {
    return;
  }

  ScanFindingsService.getRepositoryById(repositoryId.value)
    .then((response: AxiosResponse<RepositoryRead>) => {
      repository.value = response.data;
      fetchVCSInstance();
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function fetchScan() {
  loadedData.value = false;
  selectedScanID.value = Number(props.scanId);
  ScanFindingsService.getScanById(selectedScanID.value)
    .then((response: AxiosResponse<ScanRead>) => {
      repositoryId.value = response.data.repository_id;
      scanType.value = response.data.scan_type ?? '';
      incrementNumber.value = response.data.increment_number;
      fetchRepository();
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function fetchPaginatedFindingsByScanId() {
  loadedData.value = false;
  ScanFindingsService.getScanById(selectedScanID.value)
    .then((response: AxiosResponse<ScanRead>) => {
      scanType.value = response.data.scan_type;
      incrementNumber.value = response.data.increment_number;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });

  const filterObj: QueryFilterType = {
    skip: skipRowCount.value,
    limit: perPage.value,
    scanIds: [selectedScanID.value],
    findingStatus: statusFilter.value,
    rule: ruleFilter.value,
    ruleTags: ruleTagsFilter.value,
  };

  FindingsService.getDetailedFindings(filterObj)
    .then((response: AxiosResponse<PaginationType<DetailedFindingRead>>) => {
      totalRows.value = 0;
      findingList.value = [];
      selectedCheckBoxIds.value = [];
      totalRows.value = response.data.total;
      findingList.value = response.data.data;
      addScanTypeTagForSingleScan();
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function addScanTypeTagForSingleScan() {
  findingList.value.forEach((_finding, idx, theArray) => {
    theArray[idx].scanType = scanType.value;
    theArray[idx].incrementNumber = incrementNumber.value;
  });
}

function showAuditModal() {
  auditModal.value.show();
}

function updateAudit(status: FindingStatus, comment: string) {
  findingList.value.forEach((finding, idx, theArray) => {
    if (selectedCheckBoxIds.value.includes(finding.id_)) {
      theArray[idx].status = status;
      theArray[idx].comment = comment;
    }
  });
  fetchPaginatedFindingsByScanId();
  allSelected.value = false;
}

function handleFilterChange(
  scanId: number,
  rule: string[],
  status: FindingStatus[],
  ruleTags: string[]
) {
  selectedScanID.value = scanId;
  ruleFilter.value = rule;
  ruleTagsFilter.value = ruleTags;
  statusFilter.value = status;
  currentPage.value = 1;
  allSelected.value = false;
  fetchPaginatedFindingsByScanId();
}

function displayPreviousScans(
  rule: string[],
  ruleTags: string[],
  status: FindingStatus[],
  previousScanListUpdate: ScanRead[]
) {
  currentPage.value = 1;
  allSelected.value = false;
  previousScanList.value = previousScanListUpdate;
  ruleFilter.value = rule;
  ruleTagsFilter.value = ruleTags;
  statusFilter.value = status;
  fetchPreviousScanFindings();
}

function fetchPreviousScanFindings() {
  const previousScanIds = [];
  for (const scan of previousScanList.value) {
    previousScanIds.push(scan.id_);
  }

  loadedData.value = false;

  const filterObj: QueryFilterType = {
    skip: skipRowCount.value,
    limit: perPage.value,
    scanIds: previousScanIds,
    findingStatus: statusFilter.value,
    rule: ruleFilter.value,
    ruleTags: ruleTagsFilter.value,
  };

  FindingsService.getDetailedFindings(filterObj)
    .then((response) => {
      totalRows.value = 0;
      findingList.value = [];
      selectedCheckBoxIds.value = [];
      totalRows.value = response.data.total;
      findingList.value = response.data.data;
      addScanTypeTagForMultipleScans();
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function addScanTypeTagForMultipleScans() {
  previousScanList.value.forEach((scan) => {
    findingList.value.forEach((finding, idx, theArray) => {
      if (scan.id_ === finding.scan_id) {
        theArray[idx].scanType = scan.scan_type;
        theArray[idx].incrementNumber = scan.increment_number;
      }
    });
  });
}

fetchScan();
</script>
