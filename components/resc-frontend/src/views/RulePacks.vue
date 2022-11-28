<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">RULEPACKS</small></h3>
    </div>

    <!-- Spinner -->
    <Spinner :active="spinnerActive" />

    <div class="ml-3">
      <!-- Import button to upload rulepack -->
      <b-button
        class="float-left mt-2 mb-2"
        variant="prime"
        size="sm"
        @click="showRulePackUploadModal()"
        >IMPORT</b-button
      >
      <!-- RulePackUpload Modal -->
      <RulePackUploadModal
        ref="rulePackUploadModal"
        @on-file-upload-suceess="onRulePackUploadSuccess"
      />
    </div>

    <!--Rule Packs Table -->
    <div v-if="!hasRecords" class="text-center cursor-default">
      <br />
      <br />No Record Found...
    </div>

    <div class="p-3" v-if="hasRecords">
      <b-table
        id="rule-packs-table"
        sticky-header="85vh"
        :items="rulePackList"
        :fields="fields"
        :current-page="currentPage"
        :per-page="0"
        primary-key="version"
        v-model="currentItems"
        responsive
        small
        head-variant="light"
      >
        <!-- Version Column -->
        <template #cell(version)="data">
          {{ data.item.version }}
        </template>

        <!-- Active Column -->
        <template #cell(active)="data">
          <font-awesome-icon
            v-if="data.item.active"
            icon="check-circle"
            :style="{ color: 'green' }"
          />
          <font-awesome-icon v-if="!data.item.active" icon="check-circle" class="disabled-button" />
        </template>

        <!-- Download Column -->
        <template #cell(download)="data">
          <font-awesome-icon
            icon="download"
            class="download-button"
            @click="downloadRulePack(data.item.version)"
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
import Spinner from '@/components/Common/Spinner.vue';
import RulePackUploadModal from '@/components/RulePack/RulePackUploadModal.vue';
import Pagination from '@/components/Common/Pagination.vue';
import RuleService from '@/services/rule-service';
import spinnerMixin from '@/mixins/spinner.js';

export default {
  name: 'RulePacks',
  mixins: [spinnerMixin],
  data() {
    return {
      rulePackList: [],
      currentItems: [],
      totalRows: 0,
      currentPage: 1,
      perPage: Number(`${Config.value('defaultPageSize')}`),
      pageSizes: [20, 50, 100],
      requestedPageNumber: 1,
      fields: [
        {
          key: 'version',
          sortable: true,
          label: 'Version',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'active',
          sortable: true,
          label: 'Active',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'download',
          sortable: false,
          label: 'Download',
          class: 'text-left position-sticky',
          thStyle: { borderTop: '0px' },
        },
      ],
    };
  },
  computed: {
    hasRecords() {
      return this.rulePackList.length > 0;
    },
  },
  methods: {
    handlePageClick(page) {
      this.currentPage = page;
      this.fetchPaginatedRulePacks();
    },
    handlePageSizeChange(pageSize) {
      this.perPage = Number(pageSize);
      this.currentPage = 1;
      this.fetchPaginatedRulePacks();
    },
    showRulePackUploadModal() {
      this.$refs.rulePackUploadModal.show();
    },
    onRulePackUploadSuccess() {
      this.fetchPaginatedRulePacks();
    },
    fetchPaginatedRulePacks() {
      this.showSpinner();
      RuleService.getRulePacks()
        .then((response) => {
          this.rulePackList = response.data.data.sort().reverse();
          this.totalRows = response.data.total;
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    forceFileDownload(response, title) {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', title);
      document.body.appendChild(link);
      link.click();
    },
    downloadRulePack(rulePackVersion) {
      this.showSpinner();
      const title = `RESC-SECRETS-RULE_v${rulePackVersion}.TOML`;
      RuleService.downloadRulePack(rulePackVersion)
        .then((response) => {
          this.forceFileDownload(response, title);
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
  },

  created() {
    this.fetchPaginatedRulePacks();
  },
  components: {
    Pagination,
    RulePackUploadModal,
    Spinner,
  },
};
</script>
