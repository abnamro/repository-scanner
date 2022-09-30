<template>
  <div>
    <b-badge v-if="scanType == 'BASE'" variant="success">{{ baseScanTag }}</b-badge>
    <b-badge v-if="scanType == 'INCREMENTAL'" variant="info">INC: {{ incrementNumber }}</b-badge>
  </div>
</template>
<script>
export default {
  name: 'ScanTypeBadge',
  props: {
    scanType: {
      type: String,
      required: true,
    },
    incrementNumber: {
      type: Number,
      required: true,
    },
  },
  computed: {
    baseScanTag() {
      const baseScanTag = this.incrementNumber > 0 ? `BASE: ${this.incrementNumber}` : 'BASE';
      return baseScanTag;
    },
    incrementalScanTag() {
      const incrementalScanTag = this.incrementNumber > 0 ? `INC: ${this.incrementNumber}` : 'INC';
      return incrementalScanTag;
    },
  },
};
</script>
