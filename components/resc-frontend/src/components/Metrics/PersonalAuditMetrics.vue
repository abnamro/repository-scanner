<template>
  <div>
    <!-- Spinner -->
    <Spinner :active="spinnerActive" />

    <!-- Audit Activity Over Time -->
    <div>
      <div class="col-md-2 pt-4 page-title">
        <h5 class="text-nowrap">Audit Activity Over Time</h5>
      </div>

      <div class="pt-2 mr-2">
        <b-card-group class="col-md-12" deck>
          <Card
            :cardTitle="todayAuditTitle"
            :cardBodyContent="todayAuditCount"
            :titleIcon="tootltipIcon"
            :titleIconColor="tootltipIconColor"
            :titleIconTooltip="todayAuditTooltip"
          />
          <Card
            :cardTitle="currentWeekAuditTitle"
            :cardBodyContent="currentWeekAuditCount"
            :titleIcon="tootltipIcon"
            :titleIconColor="tootltipIconColor"
            :titleIconTooltip="currentWeekAuditTooltip"
          />
          <Card
            :cardTitle="currentMonthAuditTitle"
            :cardBodyContent="currentMonthAuditCount"
            :titleIcon="tootltipIcon"
            :titleIconColor="tootltipIconColor"
            :titleIconTooltip="currentMonthAuditTooltip"
          />
          <Card
            :cardTitle="currentYearAuditTitle"
            :cardBodyContent="currentYearAuditCount"
            :titleIcon="tootltipIcon"
            :titleIconColor="tootltipIconColor"
            :titleIconTooltip="currentYearAuditTooltip"
          />
          <Card
            :cardTitle="allTimeAuditTitle"
            :cardBodyContent="allTimeAuditCount"
            :titleIcon="tootltipIcon"
            :titleIconColor="tootltipIconColor"
            :titleIconTooltip="allTimeAuditTooltip"
          />
        </b-card-group>
      </div>
    </div>

    <div>
      <div class="row ml-1 pt-1">
        <!-- Audit Trend -->
        <div>
          <div class="col-md-2 pt-5 page-title">
            <h5 class="text-nowrap">Audit Trend</h5>
          </div>

          <b-card-group class="col-md-12" deck>
            <Card
              :cardTitle="currentWeekAuditTrendTitle"
              :cardBodyContent="currentWeekAuditTrendPercentageCount"
              :contentColor="currentWeekAuditTrendContentColor"
              :contentIcon="currentWeekAuditTrendIcon"
              :contentIconColor="currentWeekAuditTrendIconColor"
              :titleIcon="tootltipIcon"
              :titleIconColor="tootltipIconColor"
              :titleIconTooltip="currentWeekAuditTrendTooltip"
            />
          </b-card-group>
        </div>

        <!-- Audit Rank -->
        <div>
          <div class="col-md-2 pt-5 page-title">
            <h5 class="text-nowrap">Audit Rank</h5>
          </div>

          <b-card-group class="col-md-12" deck>
            <Card
              :cardTitle="weeklyRankTitle"
              :cardBodyContent="weeklyRankLabel"
              :contentColor="weeklyRankContentColor"
              :contentIcon="weeklyRankIcon"
              :contentIconColor="weeklyRankIconColor"
              :titleIcon="tootltipIcon"
              :titleIconColor="tootltipIconColor"
              :titleIconTooltip="weeklyRankTooltip"
            />
          </b-card-group>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import AxiosConfig from '@/configuration/axios-config.js';
import Card from '@/components/Common/Card.vue';
import DateUtils from '@/utils/date-utils';
import MetricsService from '@/services/metrics-service';
import Spinner from '@/components/Common/Spinner.vue';
import spinnerMixin from '@/mixins/spinner.js';

export default {
  name: 'PersonalAuditMetrics',
  mixins: [spinnerMixin],
  data() {
    return {
      lastWeekAuditCount: 0,

      todayAuditTitle: 'Today',
      todayAuditCount: 0,
      todayAuditTooltip: 'Total number of findings you triaged today',

      currentWeekAuditTitle: 'Current Week',
      currentWeekAuditCount: 0,
      currentWeekAuditTooltip: 'Total number of findings you triaged this week',

      currentMonthAuditTitle: `${DateUtils.getCurrentMonth()}-${DateUtils.getCurrentYear()}`,
      currentMonthAuditCount: 0,
      currentMonthAuditTooltip: 'Total number of findings you triaged this month',

      currentYearAuditTitle: `Year-${DateUtils.getCurrentYear()}`,
      currentYearAuditCount: 0,
      currentYearAuditTooltip: 'Total number of findings you triaged this year',

      allTimeAuditTitle: 'All Time',
      allTimeAuditCount: 0,
      allTimeAuditTooltip: 'Total number of findings you triaged till date',

      currentWeekAuditTrendTitle: 'Current Week',
      currentWeekAuditTrendPercentageCount: '0%',
      currentWeekAuditTrendIcon: null,
      currentWeekAuditTrendIconColor: null,
      currentWeekAuditTrendContentColor: null,
      currentWeekAuditTrendTooltip: 'Your audit trend this week in comparison to last week',

      weeklyRankTitle: 'Current Week',
      weeklyRankValue: 0,
      weeklyRankLabel: null,
      weeklyRankIcon: null,
      weeklyRankIconColor: null,
      weeklyRankContentColor: null,
      weeklyRankTooltip: 'Your rank based on number of findings you triaged in current week',

      tootltipIcon: 'info-circle',
      tootltipIconColor: '#948C8C',
    };
  },
  methods: {
    isDecimal(number) {
      return number % 1 !== 0;
    },
    formatPercentageChange(percentage) {
      return this.isDecimal(percentage) ? percentage.toFixed(2) : percentage.toLocaleString();
    },
    formatWeeklyRankLabel(rank) {
      return rank ? this.convertToRank(rank) : 'No Activity';
    },
    calculateAuditTrendInPercentage() {
      let percentageChange = 0;
      if (!this.currentWeekAuditCount && !this.lastWeekAuditCount) {
        percentageChange = 0;
      } else if (!this.lastWeekAuditCount && this.currentWeekAuditCount) {
        percentageChange = 100;
      } else {
        percentageChange =
          ((this.currentWeekAuditCount - this.lastWeekAuditCount) / this.lastWeekAuditCount) * 100;
      }
      percentageChange = this.formatPercentageChange(percentageChange);

      if (percentageChange < 0) {
        this.currentWeekAuditTrendIcon = 'arrow-down';
        this.currentWeekAuditTrendIconColor = 'red';
        this.currentWeekAuditTrendContentColor = 'red';
      } else if (percentageChange > 0) {
        this.currentWeekAuditTrendIcon = 'arrow-up';
        this.currentWeekAuditTrendIconColor = 'green';
        this.currentWeekAuditTrendContentColor = 'green';
      }
      return `${percentageChange}%`;
    },
    setIconsForAuditRank(rank) {
      if (rank === 0) {
        this.weeklyRankIcon = 'thumbs-down';
        this.weeklyRankIconColor = 'red';
        this.weeklyRankContentColor = 'red';
        this.weeklyRankValue = 'No Activity';
      } else if (rank === 1) {
        this.weeklyRankIcon = 'trophy';
        this.weeklyRankIconColor = '#FFC107';
        this.weeklyRankContentColor = '#FFC107';
      } else if (rank === 2) {
        this.weeklyRankIcon = 'medal';
        this.weeklyRankIconColor = '#B87333';
        this.weeklyRankContentColor = '#B87333';
      } else if (rank === 3) {
        this.weeklyRankIcon = 'award';
        this.weeklyRankIconColor = '#00BFFF';
        this.weeklyRankContentColor = '#00BFFF';
      }
    },
    convertToRank(number) {
      let suffix = '';
      if (number % 100 >= 11 && number % 100 <= 13) {
        suffix = 'th';
      } else {
        switch (number % 10) {
          case 1:
            suffix = 'st';
            break;
          case 2:
            suffix = 'nd';
            break;
          case 3:
            suffix = 'rd';
            break;
          default:
            suffix = 'th';
            break;
        }
      }
      return number + suffix;
    },
    getPersonalAuditMetrics() {
      this.showSpinner();
      MetricsService.getPersonalAuditMetrics()
        .then((response) => {
          this.todayAuditCount = response.data.today;
          this.currentWeekAuditCount = response.data.current_week;
          this.lastWeekAuditCount = response.data.last_week;
          this.currentMonthAuditCount = response.data.current_month;
          this.currentYearAuditCount = response.data.current_year;
          this.allTimeAuditCount = response.data.forever;
          this.weeklyRankValue = response.data.rank_current_week;
          this.weeklyRankLabel = this.formatWeeklyRankLabel(this.weeklyRankValue);

          this.currentWeekAuditTrendPercentageCount = this.calculateAuditTrendInPercentage();
          this.setIconsForAuditRank(this.weeklyRankValue);
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
  },
  created() {
    this.getPersonalAuditMetrics();
  },
  components: {
    Card,
    Spinner,
  },
};
</script>
