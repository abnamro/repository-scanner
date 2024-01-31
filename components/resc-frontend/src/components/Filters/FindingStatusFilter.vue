<template>
  <div>
    <b-form-group class="label-title text-start" label="Status" label-for="status-filter">
      <multiselect
        v-model="selectedStatus"
        :options="optionsStatus"
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
        @update:modelValue="onStatusFilterChange"
      >
        <template v-slot:noResult><span>No status found</span></template>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import CommonUtils, { type StatusOptionType } from '@/utils/common-utils';
import Multiselect from 'vue-multiselect';
import ScanFindingsService from '@/services/scan-findings-service';
import { ref } from 'vue';
import type { FindingStatus } from '@/services/shema-to-types';

type Props = {
  statusOptions?: StatusOptionType[];
  statusSelected?: StatusOptionType[];
};

const props = withDefaults(defineProps<Props>(), {
  statusOptions: () => [],
  statusSelected: () => [],
});

const optionsStatus = ref(props.statusOptions);
const selectedStatus = ref(props.statusSelected);

const emit = defineEmits(['on-findings-status-change']);

function onStatusFilterChange() {
  if (selectedStatus.value.length > 0) {
    const statusValues: FindingStatus[] = [];
    for (const status of selectedStatus.value) {
      statusValues.push(status.value);
    }
    emit('on-findings-status-change', statusValues);
  } else {
    emit('on-findings-status-change', []);
  }
}

ScanFindingsService.getStatusList()
  .then((response) => {
    optionsStatus.value = CommonUtils.parseStatusOptions(response.data as FindingStatus[]);
  })
  .catch((error) => {
    AxiosConfig.handleError(error);
  });
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
