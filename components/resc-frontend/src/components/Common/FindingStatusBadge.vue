<template>
  <div>
    <b-badge v-if="props.status == 'NOT_ANALYZED'" variant="secondary">Not Analyzed</b-badge>
    <b-badge v-if="props.status == 'UNDER_REVIEW'" class="badge bg-info">Under Review</b-badge>
    <b-badge v-if="props.status == 'CLARIFICATION_REQUIRED'" variant="warning"
      >Clarification Required</b-badge
    >
    <b-badge v-if="props.status == 'TRUE_POSITIVE'" variant="danger">True Positive</b-badge>
    <b-badge v-if="props.status == 'FALSE_POSITIVE'" variant="success">False Positive</b-badge>
  </div>
</template>
<script setup lang="ts">
import type { FindingStatus } from '@/services/shema-to-types';
type Props = { status: FindingStatus };
const props = defineProps<Props>();
</script>
