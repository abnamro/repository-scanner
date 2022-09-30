<script>
import { Line } from 'vue-chartjs/legacy';

export default {
  name: 'LineChart',
  extends: Line,
  props: {
    chartData: {
      type: Array,
      required: false,
    },
    chartLabels: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      options: {
        responsive: true,
        maintainAspectRatio: false,
      },
    };
  },
  mounted() {
    this.renderChart(
      {
        labels: this.chartLabels,
        datasets: [
          {
            label: 'Finding Count',
            borderColor: '#249EBF',
            pointBackgroundColor: 'white',
            borderWidth: 1,
            pointBorderColor: '#249EBF',
            backgroundColor: '#249EBF',
            data: this.chartData,
          },
        ],
      },
      this.options
    );
  },
};
</script>
