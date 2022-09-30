<template>
  <div>
    <!-- Page Title -->
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">ANALYTICS</small></h3>
    </div>

    <div class="row pl-5 mt-4">
      <!-- Findings per Week Line Chart -->
      <div class="col-md-6">
        <FindingsPerWeekChart />
      </div>
    </div>
  </div>
</template>
<script>
import FindingsPerWeekChart from '@/components/AnalyticsCharts/FindingsPerWeekChart.vue';
export default {
  name: 'Analytics',
  components: {
    FindingsPerWeekChart,
  },
};
</script>
