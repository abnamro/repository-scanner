<template>
  <div>
    <b-card no-body class="text-left card-color">
      <b-tabs pills card>
        <FindingTab :finding="finding" :repository="repository"></FindingTab>
      </b-tabs>
    </b-card>
  </div>
</template>

<script>
import FindingTab from '@/components/ScanFindings/FindingTab.vue';

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
  components: { FindingTab },
};
</script>
