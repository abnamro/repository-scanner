<template>
  <div>
    <b-form-group class="label-title text-left" label="Status" label-for="status-filter">
      <multiselect
        v-model="selectedStatusList"
        :options="statusList"
        :multiple="true"
        :show-labels="true"
        :close-on-select="true"
        :clear-on-select="false"
        :searchable="true"
        :preserve-search="true"
        :select-label="'Select'"
        :deselect-label="'Remove'"
        placeholder="Select Status"
        label="label"
        track-by="id"
        :preselect-first="false"
        @input="onStatusFilterChange"
      >
        <span slot="noResult">No status found</span>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script>
import AxiosConfig from '@/configuration/axios-config.js';
import Multiselect from 'vue-multiselect';
import ScanFindingsService from '@/services/scan-findings-service';

export default {
  name: 'FindingStatusFilter',
  data() {
    return {
      statusList: [],
      selectedStatusList: [],
    };
  },
  methods: {
    onStatusFilterChange() {
      if (this.selectedStatusList.length > 0) {
        const statusValues = [];
        for (const status of this.selectedStatusList) {
          statusValues.push(status.value);
        }
        this.$emit('on-findings-status-change', statusValues);
      } else {
        this.$emit('on-findings-status-change', null);
      }
    },
    fetchStatuses() {
      ScanFindingsService.getStatusList()
        .then((response) => {
          this.statusList = ScanFindingsService.parseStatusOptions(response.data);
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
  },
  created() {
    this.fetchStatuses();
  },
  components: {
    Multiselect,
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
