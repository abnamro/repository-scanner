<template>
  <div>
    <b-tab title="HISTORY" title-item-class="tab-pills" v-on:click="fetchAuditsForFinding">
      <SpinnerVue v-if="!loadedData" />

      <!--Audit History Table -->
      <div v-if="!hasRecords && loadedData" class="text-center cursor-default">
        <br />
        <br />No Record Found...
      </div>

      <div class="pr-1" v-if="hasRecords">
        <!-- sticky-header="230px" -->
        <b-table
          id="audit-history-table"
          :sticky-header="true"
          :items="auditList"
          :fields="fields"
          :current-page="currentPage"
          :per-page="0"
          v-model="currentItems"
          small
          head-variant="light"
        >
          <!-- Timestamp Column -->
          <template #cell(timestamp)="data">
            {{ formatDate((data.item as AuditRead).timestamp) }}
          </template>

          <!-- Auditor Column -->
          <template #cell(auditor)="data">
            {{ (data.item as AuditRead).auditor }}
          </template>

          <!-- Status Column -->
          <template #cell(status)="data">
            {{ parseStatus((data.item as AuditRead).status) }}
          </template>

          <!-- Comment Column -->
          <template #cell(comment)="data">
            <p
              v-if="(data.item as AuditRead).comment && ((data.item as AuditRead)?.comment?.length ?? 0) > 45"
              v-b-popover.hover="(data.item as AuditRead).comment"
              class="elipsis"
            >
              {{ (data.item as AuditRead).comment }}
            </p>
            <p v-else>{{ (data.item as AuditRead).comment }}</p>
          </template>
        </b-table>
      </div>
    </b-tab>
  </div>
</template>

<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import DateUtils from '@/utils/date-utils';
import CommonUtils from '@/utils/common-utils';
import FindingsService from '@/services/findings-service';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import type { AuditRead, DetailedFindingRead, FindingStatus } from '@/services/shema-to-types';
import { computed, ref } from 'vue';

const loadedData = ref(false);

type Props = {
  finding: DetailedFindingRead;
};
const props = defineProps<Props>();

const finding = ref(props.finding);
const auditList = ref([] as AuditRead[]);
const currentItems = ref([]);
const totalRows = ref(0);
const currentPage = ref(1);
const fields = ref([
  {
    key: 'timestamp',
    sortable: true,
    label: 'Date',
    class: 'text-start position-sticky small',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'auditor',
    sortable: false,
    label: 'Auditor',
    class: 'text-start position-sticky small',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'status',
    sortable: false,
    label: 'Status',
    class: 'text-start position-sticky small',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'comment',
    sortable: false,
    label: 'Comment',
    class: 'text-start position-sticky small',
    thStyle: { borderTop: '0px' },
  },
]);

const hasRecords = computed(() => {
  return auditList.value.length > 0;
});

function formatDate(timestamp: string): string {
  return DateUtils.formatDate(timestamp);
}

function parseStatus(input: FindingStatus): string {
  return CommonUtils.formatStatusLabels(input);
}

function fetchAuditsForFinding() {
  loadedData.value = false;
  FindingsService.getFindingAudits(finding.value.id_, 100, 0)
    .then((response) => {
      auditList.value = response.data.data;
      totalRows.value = response.data.total;
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}
</script>
<style>
.elipsis {
  text-overflow: ellipsis;
}
</style>
