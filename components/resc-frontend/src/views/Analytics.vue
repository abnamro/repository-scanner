<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">ANALYTICS</small></h3>
    </div>

    <!-- Personal Audit Metrics -->
    <PersonalAuditMetrics></PersonalAuditMetrics>
  </div>
</template>
<script>
import PersonalAuditMetrics from '@/components/Metrics/PersonalAuditMetrics.vue';

export default {
  name: 'Analytics',
  components: {
    PersonalAuditMetrics,
  },
};
</script>
