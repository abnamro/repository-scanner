<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-start page-title">
      <h3><small class="text-nowrap">RULEPACKS</small></h3>
    </div>

    <SpinnerVue v-if="!loadedData" />

    <div class="ml-3">
      <!-- Import button to upload rulepack -->
      <b-button
        class="float-left mt-2 mb-2"
        variant="primary"
        size="sm"
        v-on:click="showRulePackUploadModal()"
        >IMPORT</b-button
      >
      <!-- RulePackUpload Modal -->
      <RulePackUploadModal
        ref="rulePackUploadModal"
        @on-file-upload-suceess="onRulePackUploadSuccess"
      />
    </div>

    <!--Rule Packs Table -->
    <div v-if="!hasRecords && loadedData" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <div class="p-3" v-if="hasRecords">
      <!-- sticky-header="85vh" -->
      <b-table
        id="rule-packs-table"
        :items="rulePackList"
        :sticky-header="true"
        :fields="fields"
        :current-page="1"
        :per-page="0"
        primary-key="version"
        v-model="currentItems"
        responsive
        small
        head-variant="light"
      >
        <!-- Version Column -->
        <template #cell(version)="data">
          {{ (data.item as RulePackRead).version }}
        </template>

        <!-- Active Column -->
        <template #cell(active)="data">
          <FontAwesomeIcon
            v-if="(data.item as RulePackRead).active"
            icon="check-circle"
            :style="{ color: 'green' }"
          />
          <FontAwesomeIcon
            v-if="!(data.item as RulePackRead).active"
            icon="check-circle"
            class="disabled-button"
          />
        </template>

        <!-- Download Column -->
        <template #cell(download)="data">
          <FontAwesomeIcon
            icon="download"
            class="download-button"
            v-on:click="downloadRulePack((data.item as RulePackRead).version)"
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
import DateUtils from '@/utils/date-utils';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import RulePackUploadModal from '@/components/RulePack/RulePackUploadModal.vue';
import Pagination from '@/components/Common/PaginationVue.vue';
import RulePackService from '@/services/rule-pack-service';
import { computed, ref } from 'vue';
import type { AxiosResponse } from 'axios';
import type { PaginationType, RulePackRead } from '@/services/shema-to-types';
import type { TableItem } from 'bootstrap-vue-next';
import type { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

const loadedData = ref(false);
const rulePackUploadModal = ref();

const rulePackList = ref([] as RulePackRead[]);
const currentItems = ref([] as TableItem[]);
const totalRows = ref(0);
const currentPage = ref(1);
const perPage = ref(Number(`${Config.value('defaultPageSize')}`));
const pageSizes = ref([20, 50, 100]);
const requestedPageNumber = ref(1);
const fields = ref([
  {
    key: 'version',
    sortable: true,
    label: 'Version',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'active',
    sortable: true,
    label: 'Active',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
  {
    key: 'created',
    sortable: true,
    label: 'Created',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
    formatter: 'formatDate',
  },
  {
    key: 'download',
    sortable: false,
    label: 'Download',
    class: 'text-start position-sticky',
    thStyle: { borderTop: '0px' },
  },
]);

const hasRecords = computed(() => rulePackList.value.length > 0);

function handlePageClick(page: number) {
  currentPage.value = page;
  fetchPaginatedRulePacks();
}

function handlePageSizeChange(pageSize: number) {
  perPage.value = pageSize;
  currentPage.value = 1;
  fetchPaginatedRulePacks();
}
function showRulePackUploadModal() {
  rulePackUploadModal.value.show();
}
function onRulePackUploadSuccess() {
  fetchPaginatedRulePacks();
}

function fetchPaginatedRulePacks() {
  loadedData.value = false;
  RulePackService.getRulePackVersions()
    .then((response: AxiosResponse<PaginationType<RulePackRead>>) => {
      rulePackList.value = response.data.data;
      totalRows.value = response.data.total;
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function forceFileDownload(response: AxiosResponse<unknown>, title: string) {
  const url = window.URL.createObjectURL(new Blob([response.data] as BlobPart[]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', title);
  document.body.appendChild(link);
  link.click();
}

function downloadRulePack(rulePackVersion: string) {
  loadedData.value = false;
  const title = `RESC-SECRETS-RULE_v${rulePackVersion}.TOML`;
  RulePackService.downloadRulePack(rulePackVersion)
    .then((response) => {
      forceFileDownload(response, title);
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

// Used in code above
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function formatDate(timestamp: number) {
  const date = DateUtils.formatDate(timestamp);
  return timestamp ? date : 'Not Available';
}

fetchPaginatedRulePacks();
</script>
