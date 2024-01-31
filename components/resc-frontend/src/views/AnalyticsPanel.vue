<template>
  <!-- Page Title -->
  <div class="ms-3 col-md-2 pt-2 text-start page-title">
    <h3><small class="text-nowrap">ANALYTICS</small></h3>
  </div>

  <!-- Personal Audit Metrics -->
  <PersonalAuditMetrics></PersonalAuditMetrics>
</template>
<script setup lang="ts">
import PersonalAuditMetrics from '@/components/Metrics/PersonalAuditMetrics.vue';
</script>
