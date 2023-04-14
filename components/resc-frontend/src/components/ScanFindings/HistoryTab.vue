<template>
  <div>
    <b-tab title="HISTORY" title-item-class="tab-pills" @click="fetchAuditsForFinding">
      <!-- Spinner -->
      <Spinner :active="spinnerActive" />

      <!--Audit History Table -->
      <div v-if="!hasRecords" class="text-center cursor-default">
        <br />
        <br />No Record Found...
      </div>

      <div class="pr-1" v-if="hasRecords">
        <b-table
          id="audit-history-table"
          sticky-header="230px"
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
            {{ formatDate(data.item.timestamp) }}
          </template>

          <!-- Auditor Column -->
          <template #cell(auditor)="data">
            {{ data.item.auditor }}
          </template>

          <!-- Status Column -->
          <template #cell(status)="data">
            {{ parseStatus(data.item.status) }}
          </template>

          <!-- Comment Column -->
          <template #cell(comment)="data">
            <p
              v-if="data.item.comment && data.item.comment.length > 45"
              v-b-popover.hover="data.item.comment"
            >
              {{ truncate(data.item.comment, 45, '...') }}
            </p>
            <p v-else>{{ data.item.comment }}</p>
          </template>
        </b-table>
      </div>
    </b-tab>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import Config from '@/configuration/config';
import DateUtils from '@/utils/date-utils';
import FindingsService from '@/services/findings-service';
import Spinner from '@/components/Common/Spinner.vue';
import spinnerMixin from '@/mixins/spinner.js';

export default {
  name: 'HistoryTab1',
  mixins: [spinnerMixin],
  props: {
    finding: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      auditList: [],
      currentItems: [],
      totalRows: 0,
      currentPage: 1,
      perPage: Number(`${Config.value('defaultPageSize')}`),
      pageSizes: [20, 50, 100],
      requestedPageNumber: 1,
      fields: [
        {
          key: 'timestamp',
          sortable: true,
          label: 'Date',
          class: 'text-left position-sticky small',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'auditor',
          sortable: false,
          label: 'Auditor',
          class: 'text-left position-sticky small',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'status',
          sortable: false,
          label: 'Status',
          class: 'text-left position-sticky small',
          thStyle: { borderTop: '0px' },
        },
        {
          key: 'comment',
          sortable: false,
          label: 'Comment',
          class: 'text-left position-sticky small',
          thStyle: { borderTop: '0px' },
        },
      ],
    };
  },
  computed: {
    hasRecords() {
      return this.auditList.length > 0;
    },
  },
  methods: {
    handlePageClick(page) {
      this.currentPage = page;
      this.fetchPaginatedAuditHistoryForFinding();
    },
    handlePageSizeChange(pageSize) {
      this.perPage = Number(pageSize);
      this.currentPage = 1;
      this.fetchPaginatedAuditHistoryForFinding();
    },
    formatDate(timestamp) {
      return DateUtils.formatDate(timestamp);
    },
    truncate: function (text, length, suffix) {
      if (text.length > length) {
        return text.substring(0, length) + suffix;
      } else {
        return text;
      }
    },
    parseStatus(input) {
      let status;
      if (input === 'NOT_ANALYZED') {
        status = 'Not Analyzed';
      } else if (input === 'UNDER_REVIEW') {
        status = 'Under Review';
      } else if (input === 'CLARIFICATION_REQUIRED') {
        status = 'Clarification Required';
      } else if (input === 'TRUE_POSITIVE') {
        status = 'True Positive';
      } else if (input === 'FALSE_POSITIVE') {
        status = 'False Positive';
      }
      return status;
    },
    fetchAuditsForFinding() {
      this.showSpinner();
      FindingsService.getFindingAudits(this.finding.id_, 100, 0)
        .then((response) => {
          this.auditList = response.data.data;
          this.totalRows = response.data.total;
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
  },
  created() {},
  components: {
    Spinner,
  },
};
</script>
