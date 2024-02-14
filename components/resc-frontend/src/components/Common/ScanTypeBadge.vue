<template>
  <div>
    <b-badge v-if="props.scanType == 'BASE'" variant="success">{{ baseScanTag }}</b-badge>
    <b-badge v-if="props.scanType == 'INCREMENTAL'" variant="info"
      >INC: {{ props.incrementNumber }}</b-badge
    >
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue';
type Props = {
  scanType: string;
  incrementNumber: number;
};
const props = defineProps<Props>();

const baseScanTag = computed(() =>
  props.incrementNumber > 0 ? `BASE: ${props.incrementNumber}` : 'BASE',
);
</script>
