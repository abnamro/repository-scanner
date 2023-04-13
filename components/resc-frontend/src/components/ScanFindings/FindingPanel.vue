<template>
  <div>
    <div class="row text-left">
      <!-- Finding info -->
      <div class="col-md-5">
        <b-card-text
          ><span class="font-weight-bold">Commit ID: </span
          ><a class="custom-link" v-bind:href="finding.commit_url" target="_blank">{{
            finding.commit_id
          }}</a></b-card-text
        >
        <b-card-text
          ><span class="font-weight-bold">File Path: </span>{{ finding.file_path }}</b-card-text
        >
        <b-card-text
          ><span class="font-weight-bold">Line Number: </span>{{ finding.line_number }}</b-card-text
        >
        <b-card-text
          ><span class="font-weight-bold">Position: </span>{{ finding.column_start }} -
          {{ finding.column_end }}</b-card-text
        >
        <b-card-text
          ><span class="font-weight-bold">Author: </span>{{ finding.author }}</b-card-text
        >
        <b-card-text><span class="font-weight-bold">Email: </span>{{ finding.email }}</b-card-text>
        <b-card-text
          ><span class="font-weight-bold">Commit Time: </span
          >{{ finding.commit_timestamp }}</b-card-text
        >
        <b-card-text
          ><span class="font-weight-bold">Commit Message: </span
          >{{ finding.commit_message | truncate(50, '...') }}</b-card-text
        >
        <b-card-text
          ><span class="font-weight-bold">Rulepack: </span>{{ finding.rule_pack }}</b-card-text
        >
      </div>

      <!-- Audit and History Tabs -->
      <div class="col-md-7">
        <b-card no-body class="text-left card-color">
          <b-tabs pills card>
            <AuditTab :finding="finding"></AuditTab>
            <HistoryTab :finding="finding"></HistoryTab>
          </b-tabs>
        </b-card>
      </div>
    </div>
  </div>
</template>

<script>
import AuditTab from '@/components/ScanFindings/AuditTab.vue';
import HistoryTab from '@/components/ScanFindings/HistoryTab.vue';

export default {
  name: 'FindingPanel',
  props: {
    finding: {
      type: Object,
      required: true,
    },
    repository: {
      type: Object,
      required: true,
    },
  },
  filters: {
    truncate: function (text, length, suffix) {
      if (text.length > length) {
        return text.substring(0, length) + suffix;
      } else {
        return text;
      }
    },
  },
  components: { AuditTab, HistoryTab },
};
</script>
<style scoped>
.custom-link {
  color: #005e5d;
}
a:hover {
  color: #005e5d;
}
</style>
