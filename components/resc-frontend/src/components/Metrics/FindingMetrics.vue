<template>
  <div class="ms-4">
    <div class="col-md-2 pt-2 text-start page-title">
      <h3><small class="text-nowrap">Finding Metrics</small></h3>
    </div>
    <div class="pl-2">
      <div class="row">
        <div class="col-md-5 pt-2">
          <h5><small class="text-nowrap">Findings per week</small></h5>
          <SpinnerVue v-if="!loadedTotal" />
          <MultiLineChart v-if="loadedTotal" :chart-data="chartDataForTotalFindingsCountGraph" />
        </div>
        <div class="col-md-1"></div>
        <div class="col-md-5 pt-2">
          <h5><small class="text-nowrap">True positive findings per week</small></h5>
          <SpinnerVue v-if="!loadedTruePositive" />
          <MultiLineChart
            v-if="loadedTruePositive"
            :chart-data="chartDataForTruePositiveFindingsCountGraph"
          />
        </div>
      </div>

      <div class="row">
        <div class="col-md-5 mt-5 pt-2">
          <h5><small class="text-nowrap">UnTriaged findings per week</small></h5>
          <SpinnerVue v-if="!loadedUnTriaged" />
          <MultiLineChart
            v-if="loadedUnTriaged"
            :chart-data="chartDataForUnTriagedFindingsCountGraph"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import Config from '@/configuration/config';
import FindingsService from '@/services/findings-service';
import MultiLineChart from '@/components/Charts/MultiLineChartVue.vue';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import { ref } from 'vue';
import type { FindingCountOverTime } from '@/services/shema-to-types';
import type { DataSetObject } from './types';

const loadedTotal = ref(false);
const loadedTruePositive = ref(false);
const loadedUnTriaged = ref(false);

const labelsWeekTruePositive = ref([] as string[]);
const labelsWeekTotal = ref([] as string[]);
const labelsWeekUnTriaged = ref([] as string[]);
const chartDataForTotalFindingsCountGraph = ref({
  labels: [] as string[],
  datasets: [] as DataSetObject[],
});
const chartDataForTruePositiveFindingsCountGraph = ref({
  labels: [] as string[],
  datasets: [] as DataSetObject[],
});
const chartDataForUnTriagedFindingsCountGraph = ref({
  labels: [] as string[],
  datasets: [] as DataSetObject[],
});
const findingsCount = ref([] as FindingCountOverTime[]);
const azureDevOpsTotalFindingsCountList = ref([] as number[]);
const bitbucketTotalFindingsCountList = ref([] as number[]);
const gitHubTotalFindingsCountList = ref([] as number[]);
const totalTotalFindingsCountList = ref([] as number[]);
const azureDevOpsTruePositiveFindingsCountList = ref([] as number[]);
const bitbucketTruePositiveFindingsCountList = ref([] as number[]);
const gitHubTruePositiveFindingsCountList = ref([] as number[]);
const totalTruePositiveFindingsCountList = ref([] as number[]);
const azureDevOpsUnTriagedFindingsCountList = ref([] as number[]);
const bitbucketUnTriagedFindingsCountList = ref([] as number[]);
const gitHubUnTriagedFindingsCountList = ref([] as number[]);
const totalUnTriagedFindingsCountList = ref([] as number[]);

function arrayContainsAllZeros(arr: number[]) {
  return arr.every((item) => item === 0);
}

function getGraphData(): void {
  getTotalCounts();
  getTruePositiveCounts();
  getUnTriagedCounts();
}

function getTruePositiveCounts() {
  FindingsService.getTruePositiveCountPerVcsProviderPerWeek()
    .then((response) => {
      findingsCount.value = response.data;
      findingsCount.value.forEach((data) => {
        labelsWeekTruePositive.value.push(data.time_period);
        azureDevOpsTruePositiveFindingsCountList.value.push(
          data.vcs_provider_finding_count?.AZURE_DEVOPS ?? 0,
        );
        bitbucketTruePositiveFindingsCountList.value.push(
          data.vcs_provider_finding_count?.BITBUCKET ?? 0,
        );
        gitHubTruePositiveFindingsCountList.value.push(
          data.vcs_provider_finding_count?.GITHUB_PUBLIC ?? 0,
        );
        totalTruePositiveFindingsCountList.value.push(data.total ?? 0);
      });

      setChartDataForTruePositiveFindingsCount();
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function getTotalCounts() {
  FindingsService.getMetricsFindingsCountPerVcsProviderPerWeek()
    .then((response) => {
      findingsCount.value = response.data;
      findingsCount.value.forEach((data) => {
        labelsWeekTotal.value.push(data.time_period);
        azureDevOpsTotalFindingsCountList.value.push(
          data.vcs_provider_finding_count?.AZURE_DEVOPS ?? 0,
        );
        bitbucketTotalFindingsCountList.value.push(data.vcs_provider_finding_count?.BITBUCKET ?? 0);
        gitHubTotalFindingsCountList.value.push(
          data.vcs_provider_finding_count?.GITHUB_PUBLIC ?? 0,
        );
        totalTotalFindingsCountList.value.push(data.total ?? 0);
      });

      setChartDataForTotalFindingsCount();
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function getUnTriagedCounts() {
  FindingsService.getUnTriagedCountPerVcsProviderPerWeek()
    .then((response) => {
      findingsCount.value = response.data;
      findingsCount.value.forEach((data) => {
        labelsWeekUnTriaged.value.push(data.time_period);
        azureDevOpsUnTriagedFindingsCountList.value.push(
          data.vcs_provider_finding_count?.AZURE_DEVOPS ?? 0,
        );
        bitbucketUnTriagedFindingsCountList.value.push(
          data.vcs_provider_finding_count?.BITBUCKET ?? 0,
        );
        gitHubUnTriagedFindingsCountList.value.push(
          data.vcs_provider_finding_count?.GITHUB_PUBLIC ?? 0,
        );
        totalUnTriagedFindingsCountList.value.push(data.total ?? 0);
      });

      setChartDataForUnTriagedFindingsCount();
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function prepareDataSetForVcsProvider(vcsType: string, findingCountList: number[]): DataSetObject {
  let colourCode = '#ffffff';
  const datasetsObj: DataSetObject = {
    borderWidth: 1.5,
    cubicInterpolationMode: 'monotone',
    data: findingCountList,
    pointStyle: 'circle',
    pointRadius: 3,
    pointHoverRadius: 8,
  };

  if (vcsType === `${Config.value('azureDevOpsVal')}`) {
    datasetsObj.label = `${Config.value('azureDevOpsLabel')}`;
    colourCode = '#10D9A2';
  }
  if (vcsType === `${Config.value('bitbucketVal')}`) {
    datasetsObj.label = `${Config.value('bitbucketLabel')}`;
    colourCode = '#FF7F00';
  }
  if (vcsType === `${Config.value('githubPublicVal')}`) {
    datasetsObj.label = `${Config.value('githubPublicLabel')}`;
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
}

function setChartDataForTotalFindingsCount() {
  const datasets: DataSetObject[] = [];
  if (!arrayContainsAllZeros(azureDevOpsTotalFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('azureDevOpsVal')}`,
      azureDevOpsTotalFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(bitbucketTotalFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('bitbucketVal')}`,
      bitbucketTotalFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(gitHubTotalFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('githubPublicVal')}`,
      gitHubTotalFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(totalTotalFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider('Total', totalTotalFindingsCountList.value);
    datasets.push(datasetObj);
  }
  chartDataForTotalFindingsCountGraph.value['labels'] = labelsWeekTotal.value;
  chartDataForTotalFindingsCountGraph.value['datasets'] = datasets;
  loadedTotal.value = true;
}

function setChartDataForTruePositiveFindingsCount() {
  const datasets = [];
  if (!arrayContainsAllZeros(azureDevOpsTruePositiveFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('azureDevOpsVal')}`,
      azureDevOpsTruePositiveFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(bitbucketTruePositiveFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('bitbucketVal')}`,
      bitbucketTruePositiveFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(gitHubTruePositiveFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('githubPublicVal')}`,
      gitHubTruePositiveFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(totalTruePositiveFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      'Total',
      totalTruePositiveFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }
  chartDataForTruePositiveFindingsCountGraph.value['labels'] = labelsWeekTruePositive.value;
  chartDataForTruePositiveFindingsCountGraph.value['datasets'] = datasets;
  loadedTruePositive.value = true;
}

function setChartDataForUnTriagedFindingsCount() {
  const datasets = [];
  if (!arrayContainsAllZeros(azureDevOpsUnTriagedFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('azureDevOpsVal')}`,
      azureDevOpsUnTriagedFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(bitbucketUnTriagedFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('bitbucketVal')}`,
      bitbucketUnTriagedFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(gitHubUnTriagedFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider(
      `${Config.value('githubPublicVal')}`,
      gitHubUnTriagedFindingsCountList.value,
    );
    datasets.push(datasetObj);
  }

  if (!arrayContainsAllZeros(totalUnTriagedFindingsCountList.value)) {
    const datasetObj = prepareDataSetForVcsProvider('Total', totalUnTriagedFindingsCountList.value);
    datasets.push(datasetObj);
  }
  chartDataForUnTriagedFindingsCountGraph.value['labels'] = labelsWeekUnTriaged.value;
  chartDataForUnTriagedFindingsCountGraph.value['datasets'] = datasets;
  loadedUnTriaged.value = true;
}

getGraphData();
</script>
