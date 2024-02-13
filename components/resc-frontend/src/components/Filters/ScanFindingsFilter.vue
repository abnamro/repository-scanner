<template>
  <div>
    <div class="row">
      <!-- Scan Date Filter -->
      <div class="col-md-3 ml-3">
        <b-form-group class="label-title text-start" label="Scan Date" label-for="scan-date-filter">
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
            @update:modelValue="handleScanDateFilterChange"
          >
            <template v-slot:singleLabel="{ option }"
              ><span>{{ formatScanDateFilterOptions(option) }}</span></template
            >
          </multiselect>
        </b-form-group>
      </div>

      <!-- Rule Filter -->
      <div class="col-md-3">
        <RuleFilter
          ref="ruleFilterChildComponent"
          :rulesOptions="ruleList"
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
          :ruleTagsOptions="ruleTagsList"
          :ruleTagsSelected="selectedRuleTags"
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
          v-on:click="handleToggleButtonClick"
        >
          <small class="text-nowrap">Include previous scan findings</small>
        </b-form-checkbox>
      </div>
      <div class="col-md-1"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import Config from '@/configuration/config';
import DateUtils from '@/utils/date-utils';
import FindingStatusFilter from '@/components/Filters/FindingStatusFilter.vue';
import Multiselect from 'vue-multiselect';
import RuleFilter from '@/components/Filters/RuleFilter.vue';
import RulePackService from '@/services/rule-pack-service';
import RuleTagsFilter from '@/components/Filters/RuleTagsFilter.vue';
import ScanFindingsService from '@/services/scan-findings-service';
import { ref, watch, type Ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { FindingStatus, RepositoryRead, ScanRead } from '@/services/shema-to-types';

const ruleFilterChildComponent = ref();
const ruleTagsFilterChildComponent = ref();

type Props = {
  repository: RepositoryRead;
  includePreviousScans?: boolean;
};

type ScanJson = {
  scanId: number;
  scanDate: string;
  scanType: 'Incremental' | 'Base';
  rulePackVersion: string;
};

const props = withDefaults(defineProps<Props>(), {
  includePreviousScans: () => false,
});

const previousScans = ref([] as ScanRead[]);
const scanList = ref([] as ScanRead[]);
const scanDateList = ref([] as ScanJson[]);
const ruleList = ref([] as string[]);
const ruleTagsList = ref([] as string[]);
const selectedScan = ref(null) as Ref<null | ScanJson>;
const selectedRule = ref([] as string[]);
const selectedRuleTags = ref([] as string[]);
const selectedStatus = ref([] as FindingStatus[]);
const includePreviousScans = ref(props.includePreviousScans);
const skipRecords = ref(Number(`${Config.value('skipRecords')}`));
const limitRecords = ref(Number(`${Config.value('limitRecords')}`));

const router = useRouter();
const route = useRoute();
const emit = defineEmits(['previous-scans-checked', 'include-previous-scans', 'on-filter-change']);

function getPreviousScans() {
  if (selectedScan.value === null) {
    return;
  }

  for (const scan of scanList.value) {
    if (selectedScan.value.scanId >= scan.id_) {
      previousScans.value.push(scan);
      if (scan.scan_type === 'BASE') {
        break;
      }
    }
  }
}

function handleToggleButtonClick() {
  refreshRuleTagsOnToggleOfPreviousScansButton();
}

function togglePreviousScans() {
  if (includePreviousScans.value) {
    previousScans.value = [];
    getPreviousScans();
    emit('previous-scans-checked', true);
    emit(
      'include-previous-scans',
      selectedRule.value,
      selectedRuleTags.value,
      selectedStatus.value,
      previousScans.value,
    );
  } else {
    previousScans.value = [];
    emit('previous-scans-checked', false);
    handleFilterChange();
  }

  // Refresh rules in filter based on scan ids
  refreshRuleFilter();
}

function formatScanDateFilterOptions(scan: ScanJson) {
  return `${scan.scanDate}: ${scan.scanType}`;
}

function handleScanDateFilterChange() {
  // On scan date reset the Rule tags filter selection
  selectedRuleTags.value = [];
  ruleTagsFilterChildComponent.value.resetRuleTagsFilterSelection();

  // On scan date reset the Rule filter selection
  selectedRule.value = [];
  ruleFilterChildComponent.value.resetRuleFilterSelection();
  fetchRules();
}
function handleRuleFilterChange(rule: string[]) {
  selectedRule.value = rule;
  handleFilterChange();
}
function handleRuleTagsFilterChange(ruleTags: string[]) {
  selectedRuleTags.value = ruleTags;
  handleFilterChange();
}
function onStatusFilterChange(status: FindingStatus[]) {
  selectedStatus.value = status;
  handleFilterChange();
}
function handleFilterChange() {
  if (selectedScan.value === null) {
    return;
  }

  // Refresh findings
  if (!includePreviousScans.value) {
    emit(
      'on-filter-change',
      selectedScan.value.scanId,
      selectedRule,
      selectedStatus,
      selectedRuleTags,
    );
  } else {
    togglePreviousScans();
  }
}

function getPreviousScanIds() {
  const previousScanIds: number[] = [];
  for (const scan of previousScans.value) {
    previousScanIds.push(scan.id_);
  }
  const scanIds = includePreviousScans.value
    ? previousScanIds
    : selectedScan.value !== null
      ? [selectedScan.value.scanId]
      : [];
  return scanIds;
}

function getSelectedRulePacks() {
  const rulePacksForPreviousScanIds = [];
  for (const scan of previousScans.value) {
    rulePacksForPreviousScanIds.push(scan.rule_pack);
  }
  const rulePacks = includePreviousScans.value
    ? rulePacksForPreviousScanIds
    : selectedScan.value !== null
      ? [selectedScan.value.rulePackVersion]
      : [];
  return rulePacks;
}
function refreshRuleFilter() {
  const scanIds = getPreviousScanIds();
  if (scanIds.length > 0) {
    ScanFindingsService.getRulesByScanIds(scanIds)
      .then((response) => {
        selectedRule.value = [];
        ruleList.value = response.data;
      })
      .catch((error) => {
        AxiosConfig.handleError(error);
      });
  }
}

function fetchRules() {
  if (selectedScan.value === null) {
    return;
  }

  const scanIds = getPreviousScanIds();
  if (selectedScan.value.scanId && scanIds.length > 0) {
    ScanFindingsService.getRulesByScanIds(scanIds)
      .then((response) => {
        selectedRule.value = [];
        ruleList.value = response.data;

        // Fetch Rule Tags
        fetchRuleTags();
      })
      .catch((error) => {
        AxiosConfig.handleError(error);
      });
  }
}

function fetchRuleTags() {
  const rulePackVersions = getSelectedRulePacks();
  RulePackService.getRuleTagsByRulePackVersions(rulePackVersions)
    .then((response) => {
      selectedRuleTags.value = [];
      ruleTagsList.value = response.data;

      // Refresh findings
      handleFilterChange();

      // if scanId gets changed, update it in route parameter
      if (Number(route.params.scanId) !== Number(selectedScan?.value?.scanId)) {
        router.replace({
          name: 'ScanFindings',
          params: { scanId: selectedScan?.value?.scanId },
        });
      }
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}
function refreshRuleTagsOnToggleOfPreviousScansButton() {
  const rulePackVersions = getSelectedRulePacks();
  RulePackService.getRuleTagsByRulePackVersions(rulePackVersions)
    .then((response) => {
      ruleTagsList.value = response.data;
      selectedRuleTags.value = [];
      ruleTagsFilterChildComponent.value.resetRuleTagsFilterSelection();
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function fetchScanDates() {
  if (props.repository.id_) {
    ScanFindingsService.getScansByRepositoryId(
      props.repository.id_,
      skipRecords.value,
      limitRecords.value,
    )
      .then((res) => {
        const response: ScanRead[] = res.data.data;
        response.sort(function (a, b) {
          return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
        });

        scanDateList.value = [];
        scanList.value = response;

        for (const scan of scanList.value) {
          const scanJson: ScanJson = {
            scanId: scan.id_,
            scanDate: DateUtils.formatDate(scan.timestamp),
            scanType: scan.scan_type === 'INCREMENTAL' ? 'Incremental' : 'Base',
            rulePackVersion: scan.rule_pack,
          };

          // Set scan date value in select option when user clicks a record from Repositories page
          if (Number(route.params.scanId as string) === scan.id_) {
            selectedScan.value = scanJson;
          }
          scanDateList.value.push(scanJson);
        }

        //Sort scan dates
        scanDateList.value.sort(DateUtils.sortListByDate);

        //Rules depend upon scan/scan date selected
        fetchRules();
      })
      .catch((error) => {
        AxiosConfig.handleError(error);
      });
  }
}

// Double check if I work.
watch(
  () => props.repository,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  (newVal, oldVal) => {
    if (newVal !== oldVal) {
      fetchScanDates();
    }
  },
);
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
