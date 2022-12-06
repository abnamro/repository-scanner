<template>
  <div>
    <div class="col-md-2 pt-2 text-left page-title">
      <h5><small class="text-nowrap">Finding per Week</small></h5>
    </div>
    <LineChart
      v-if="loaded"
      chart-id="finding-count-weekly"
      :chart-data="findingCountWeek"
      :chart-labels="labelsWeek"
    />
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import FindingsService from '@/services/findings-service';
import LineChart from '@/components/Charts/LineChart.vue';

export default {
  name: 'FindingsPerWeekChart',
  components: {
    LineChart,
  },
  props: {},
  data() {
    return {
      findingCountWeek: [],
      labelsWeek: [],
      loaded: false,
    };
  },
  methods: {
    getFindingCountPerWeek() {
      FindingsService.getFindingCountPerWeek()
        .then((response) => {
          this.findingCountList = response.data.data;
          this.findingCountList.forEach((findingCount) => {
            this.labelsWeek.push(findingCount.date_lable);
            this.findingCountWeek.push(findingCount.finding_count);
          });
          this.loaded = true;
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
  },
  mounted() {
    this.getFindingCountPerWeek();
  },
};
</script>
