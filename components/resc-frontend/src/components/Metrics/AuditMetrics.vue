<template>
  <div>
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">Audit Metrics</small></h3>
    </div>
    <div class="pl-2">
      <h5><small class="text-nowrap">Audits by Auditor per week</small></h5>
      <Spinner :active="!loadedAuditCounts" />
      <MultiLineChart
        v-if="loadedAuditCounts"
        :chart-data="chartDataForAuditCountsGraph"
        :chart-options="chartOptions"
        :height="600"
      />
    </div>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import FindingsService from '@/services/findings-service';
import MultiLineChart from '@/components/Charts/MultiLineChart.vue';
import Spinner from '@/components/Common/Spinner.vue';

export default {
  name: 'AuditMetrics',
  components: {
    MultiLineChart,
    Spinner,
  },
  data() {
    return {
      loadedAuditCounts: false,
      loadedAuditCountsAuditors: false,
      chartDataForAuditCountsGraph: { labels: [], datasets: [] },
      auditCounts: [],
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  methods: {
    arrayContainsAllZeros(arr) {
      return arr.every((item) => item === 0);
    },
    getGraphData() {
      FindingsService.getAuditsByAuditorPerWeek()
        .then((response) => {
          this.auditCounts = response.data;
          let datasets = {};
          this.auditCounts.forEach((data) => {
            this.chartDataForAuditCountsGraph['labels'].push(data.time_period);

            if (!this.loadedAuditCountsAuditors) {
              Object.entries(data.audit_by_auditor_count).forEach((auditorData) => {
                datasets[auditorData[0]] = this.prepareDataSet(auditorData[0], auditorData[1]);
              });
              datasets['Total'] = this.prepareDataSet('Total', data.total);
              this.loadedAuditCountsAuditors = true;
            } else {
              Object.entries(data.audit_by_auditor_count).forEach((auditorData) => {
                datasets[auditorData[0]].data.push(auditorData[1]);
              });
              datasets['Total'].data.push(data.total);
            }
          });
          Object.entries(datasets).forEach((auditorDataset) => {
            this.chartDataForAuditCountsGraph.datasets.push(auditorDataset[1]);
          });
          this.loadedAuditCounts = true;
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    prepareDataSet(datasetLabel, datasetFirstValue) {
      const datasetsObj = {};
      let colourCode = '#' + Math.floor(Math.random() * 16777215).toString(16);
      datasetsObj.borderWidth = 1.5;
      datasetsObj.cubicInterpolationMode = 'monotone';
      datasetsObj.data = [datasetFirstValue];
      datasetsObj.pointStyle = 'circle';
      datasetsObj.pointRadius = 3;
      datasetsObj.pointHoverRadius = 8;
      datasetsObj.label = datasetLabel;

      if (datasetLabel === 'Total') {
        datasetsObj.hidden = true;
      }
      datasetsObj.borderColor = colourCode;
      datasetsObj.pointBackgroundColor = colourCode;
      datasetsObj.backgroundColor = colourCode;

      return datasetsObj;
    },
  },
  mounted() {
    this.getGraphData();
  },
};
</script>
