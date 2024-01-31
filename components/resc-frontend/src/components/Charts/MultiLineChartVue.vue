<template>
  <Line
    ref="multiline"
    :data="chartData"
    :styles="styles"
    :chartId="chartId"
    :cssClasses="cssClasses"
    :options="chartOptions"
  />
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { Line } from 'vue-chartjs';
import type { DataSetObject } from '../Metrics/types';
import type { ChartData, ChartOptions } from 'chart.js';

type Props = {
  chartData: { labels: string[]; datasets: DataSetObject[] };
  chartId?: string;
  width?: number;
  height?: number;
  cssClasses?: string;
  styles?: object;
};

const props = withDefaults(defineProps<Props>(), {
  chartId: 'multi-line-chart',
  width: 100,
  height: 300,
  cssClasses: '',
  styles: () => {
    return {};
  },
});

const chartData = ref(props.chartData as ChartData<'line', number[], string>);

const chartOptions: ChartOptions<'line'> = {
  responsive: true,
  // maintainAspectRatio: false, // breaks the graph
};
const chartId = ref(props.chartId);
const cssClasses = ref(props.cssClasses);
const styles =
  props.styles === undefined
    ? ref({
        height: props.height + ' px',
        width: props.width + ' px',
      })
    : ref(props.styles);
</script>
