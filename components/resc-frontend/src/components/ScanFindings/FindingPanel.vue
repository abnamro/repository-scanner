<template>
  <div>
    <div class="row text-start">
      <!-- Finding info -->
      <div class="col-md-5">
        <b-card-text
          ><span class="fw-bold">Commit ID: </span
          ><a class="custom-link" v-bind:href="findingRef.commit_url" target="_blank">{{
            findingRef.commit_id
          }}</a></b-card-text
        >
        <b-card-text
          ><span class="fw-bold">File Path: </span>{{ findingRef.file_path }}</b-card-text
        >
        <b-card-text
          ><span class="fw-bold">Line Number: </span>{{ findingRef.line_number }}</b-card-text
        >
        <b-card-text
          ><span class="fw-bold">Position: </span>{{ findingRef.column_start }} -
          {{ findingRef.column_end }}</b-card-text
        >
        <b-card-text><span class="fw-bold">Author: </span>{{ findingRef.author }}</b-card-text>
        <b-card-text><span class="fw-bold">Email: </span>{{ findingRef.email }}</b-card-text>
        <b-card-text
          ><span class="fw-bold">Commit Time: </span>{{ findingRef.commit_timestamp }}</b-card-text
        >
        <b-card-text
          ><span class="fw-bold elipsis">Commit Message: </span
          >{{ findingRef.commit_message }}</b-card-text
        >
        <b-card-text><span class="fw-bold">Rulepack: </span>{{ findingRef.rule_pack }}</b-card-text>
      </div>

      <!-- Audit and History Tabs -->
      <div class="col-md-7">
        <b-card no-body class="text-start card-color">
          <b-tabs pills card>
            <AuditTab :finding="findingRef"></AuditTab>
            <HistoryTab :finding="findingRef"></HistoryTab>
          </b-tabs>
        </b-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AuditTab from '@/components/ScanFindings/AuditTab.vue';
import HistoryTab from '@/components/ScanFindings/HistoryTab.vue';
import type { AugmentedDetailedFindingRead } from '@/services/shema-to-types';
import { ref } from 'vue';

type Props = {
  finding: AugmentedDetailedFindingRead;
};

const props = defineProps<Props>();
const findingRef = ref(props.finding);
</script>
<style scoped>
.custom-link {
  color: #005e5d;
}
a:hover {
  color: #005e5d;
}
.elipsis {
  text-overflow: ellipsis;
}
</style>
