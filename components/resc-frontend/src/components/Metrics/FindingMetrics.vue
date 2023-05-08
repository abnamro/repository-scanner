<template>
  <div>
    <div class="col-md-2 pt-2 text-left page-title">
      <h3><small class="text-nowrap">Finding Metrics</small></h3>
    </div>
    <div class="pl-2">
      <div class="row">
        <div class="col-md-5 pt-2">
          <h5><small class="text-nowrap">Findings per week</small></h5>
          <Spinner :active="!loadedTotal" />
          <MultiLineChart
            v-if="loadedTotal"
            :chart-data="chartDataForTotalFindingsCountGraph"
            :chart-options="chartOptions"
          />
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-5 pt-2">
          <h5><small class="text-nowrap">True positive findings per week</small></h5>
          <Spinner :active="!loadedTruePositive" />
          <MultiLineChart
            v-if="loadedTruePositive"
            :chart-data="chartDataForTruePositiveFindingsCountGraph"
            :chart-options="chartOptions"
          />
        </div>
      </div>

      <div class="row">
        <div class="col-md-5 mt-5 pt-2">
          <h5><small class="text-nowrap">UnTriaged findings per week</small></h5>
          <Spinner :active="!loadedUnTriaged" />
          <MultiLineChart
            v-if="loadedUnTriaged"
            :chart-data="chartDataForUnTriagedFindingsCountGraph"
            :chart-options="chartOptions"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import FindingsService from '@/services/findings-service';
import MultiLineChart from '@/components/Charts/MultiLineChart.vue';
import Spinner from '@/components/Common/Spinner.vue';

export default {
  name: 'FindingMetrics',
  components: {
    MultiLineChart,
    Spinner,
  },
  data() {
    return {
      loadedTotal: false,
      loadedTruePositive: false,
      loadedUnTriaged: false,
      labelsWeekTruePositive: [],
      labelsWeekTotal: [],
      labelsWeekUnTriaged: [],
      chartDataForTotalFindingsCountGraph: { labels: [], datasets: [] },
      chartDataForTruePositiveFindingsCountGraph: { labels: [], datasets: [] },
      chartDataForUnTriagedFindingsCountGraph: { labels: [], datasets: [] },
      findingsCount: [],
      azureDevOpsTotalFindingsCountList: [],
      bitbucketTotalFindingsCountList: [],
      gitHubTotalFindingsCountList: [],
      totalTotalFindingsCountList: [],
      azureDevOpsTruePositiveFindingsCountList: [],
      bitbucketTruePositiveFindingsCountList: [],
      gitHubTruePositiveFindingsCountList: [],
      totalTruePositiveFindingsCountList: [],
      azureDevOpsUnTriagedFindingsCountList: [],
      bitbucketUnTriagedFindingsCountList: [],
      gitHubUnTriagedFindingsCountList: [],
      totalUnTriagedFindingsCountList: [],
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
      this.getTotalCounts();
      this.getTruePositiveCounts();
      this.getUnTriagedCounts();
    },
    getTruePositiveCounts() {
      FindingsService.getTruePositiveCountPerVcsProviderPerWeek()
        .then((response) => {
          this.findingsCount = response.data;
          this.findingsCount.forEach((data) => {
            this.labelsWeekTruePositive.push(data.time_period);
            this.azureDevOpsTruePositiveFindingsCountList.push(
              data.vcs_provider_finding_count.AZURE_DEVOPS
            );
            this.bitbucketTruePositiveFindingsCountList.push(
              data.vcs_provider_finding_count.BITBUCKET
            );
            this.gitHubTruePositiveFindingsCountList.push(
              data.vcs_provider_finding_count.GITHUB_PUBLIC
            );
            this.totalTruePositiveFindingsCountList.push(data.total);
          });

          this.setChartDataForTruePositiveFindingsCount();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    getTotalCounts() {
      FindingsService.getMetricsFindingsCountPerVcsProviderPerWeek()
        .then((response) => {
          this.findingsCount = response.data;
          this.findingsCount.forEach((data) => {
            this.labelsWeekTotal.push(data.time_period);
            this.azureDevOpsTotalFindingsCountList.push(
              data.vcs_provider_finding_count.AZURE_DEVOPS
            );
            this.bitbucketTotalFindingsCountList.push(data.vcs_provider_finding_count.BITBUCKET);
            this.gitHubTotalFindingsCountList.push(data.vcs_provider_finding_count.GITHUB_PUBLIC);
            this.totalTotalFindingsCountList.push(data.total);
          });

          this.setChartDataForTotalFindingsCount();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    getUnTriagedCounts() {
      FindingsService.getUnTriagedCountPerVcsProviderPerWeek()
        .then((response) => {
          this.findingsCount = response.data;
          this.findingsCount.forEach((data) => {
            this.labelsWeekUnTriaged.push(data.time_period);
            this.azureDevOpsUnTriagedFindingsCountList.push(
              data.vcs_provider_finding_count.AZURE_DEVOPS
            );
            this.bitbucketUnTriagedFindingsCountList.push(
              data.vcs_provider_finding_count.BITBUCKET
            );
            this.gitHubUnTriagedFindingsCountList.push(
              data.vcs_provider_finding_count.GITHUB_PUBLIC
            );
            this.totalUnTriagedFindingsCountList.push(data.total);
          });

          this.setChartDataForUnTriagedFindingsCount();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    prepareDataSetForVcsProvider(vcsType, findingCountList) {
      const datasetsObj = {};
      let colourCode = '#ffffff';
      datasetsObj.borderWidth = 1.5;
      datasetsObj.cubicInterpolationMode = 'monotone';
      datasetsObj.data = findingCountList;
      datasetsObj.pointStyle = 'circle';
      datasetsObj.pointRadius = 3;
      datasetsObj.pointHoverRadius = 8;

      if (vcsType === 'AZURE_DEVOPS') {
        datasetsObj.label = 'Azure DevOps';
        colourCode = '#10D9A2';
      }
      if (vcsType === 'BITBUCKET') {
        datasetsObj.label = 'Bitbucket';
        colourCode = '#FF7F00';
      }
      if (vcsType === 'GITHUB_PUBLIC') {
        datasetsObj.label = 'GitHub';
        colourCode = '#05CBE1';
      }
      if (vcsType === 'Total') {
        datasetsObj.label = 'Total';
        colourCode = '#03857a';
        datasetsObj.hidden = true;
      }
      datasetsObj.borderColor = colourCode;
      datasetsObj.pointBackgroundColor = colourCode;
      datasetsObj.backgroundColor = colourCode;

      return datasetsObj;
    },
    setChartDataForTotalFindingsCount() {
      const datasets = [];
      if (!this.arrayContainsAllZeros(this.azureDevOpsTotalFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'AZURE_DEVOPS',
          this.azureDevOpsTotalFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.bitbucketTotalFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'BITBUCKET',
          this.bitbucketTotalFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.gitHubTotalFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'GITHUB_PUBLIC',
          this.gitHubTotalFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.totalTotalFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'Total',
          this.totalTotalFindingsCountList
        );
        datasets.push(datasetObj);
      }
      this.chartDataForTotalFindingsCountGraph['labels'] = this.labelsWeekTotal;
      this.chartDataForTotalFindingsCountGraph['datasets'] = datasets;
      this.loadedTotal = true;
    },
    setChartDataForTruePositiveFindingsCount() {
      const datasets = [];
      if (!this.arrayContainsAllZeros(this.azureDevOpsTruePositiveFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'AZURE_DEVOPS',
          this.azureDevOpsTruePositiveFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.bitbucketTruePositiveFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'BITBUCKET',
          this.bitbucketTruePositiveFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.gitHubTruePositiveFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'GITHUB_PUBLIC',
          this.gitHubTruePositiveFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.totalTruePositiveFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'Total',
          this.totalTruePositiveFindingsCountList
        );
        datasets.push(datasetObj);
      }
      this.chartDataForTruePositiveFindingsCountGraph['labels'] = this.labelsWeekTruePositive;
      this.chartDataForTruePositiveFindingsCountGraph['datasets'] = datasets;
      this.loadedTruePositive = true;
    },
    setChartDataForUnTriagedFindingsCount() {
      const datasets = [];
      if (!this.arrayContainsAllZeros(this.azureDevOpsUnTriagedFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'AZURE_DEVOPS',
          this.azureDevOpsUnTriagedFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.bitbucketUnTriagedFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'BITBUCKET',
          this.bitbucketUnTriagedFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.gitHubUnTriagedFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'GITHUB_PUBLIC',
          this.gitHubUnTriagedFindingsCountList
        );
        datasets.push(datasetObj);
      }

      if (!this.arrayContainsAllZeros(this.totalUnTriagedFindingsCountList)) {
        const datasetObj = this.prepareDataSetForVcsProvider(
          'Total',
          this.totalUnTriagedFindingsCountList
        );
        datasets.push(datasetObj);
      }
      this.chartDataForUnTriagedFindingsCountGraph['labels'] = this.labelsWeekUnTriaged;
      this.chartDataForUnTriagedFindingsCountGraph['datasets'] = datasets;
      this.loadedUnTriaged = true;
    },
  },
  mounted() {
    this.getGraphData();
  },
};
</script>
