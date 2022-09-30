<template>
  <div>
    <b-card no-body class="text-left card-color">
      <b-tabs pills card>
        <FindingInfoTab :finding="finding" :repositoryInfo="repositoryInfo"></FindingInfoTab>
      </b-tabs>
    </b-card>
  </div>
</template>

<script>
import FindingInfoTab from '@/components/ScanFindings/FindingInfoTab.vue';

export default {
  name: 'FindingPanel',
  props: {
    finding: {
      type: Object,
      required: true,
    },
    repositoryInfo: {
      type: Object,
      required: true,
    },
  },
  components: { FindingInfoTab },
};
</script>
