<template>
  <!-- Spinner -->
  <SpinnerVue v-if="!loadedData" />

  <!-- Audit Activity Over Time -->
  <div v-if="loadedData">
    <div class="ms-3 pt-4 text-start page-title">
      <h5 class="text-nowrap">Audit Activity Over Time</h5>
    </div>

    <div class="ms-3 pt-2 me-2">
      <b-card-group class="col-md-12" deck>
        <CardVue
          :cardTitle="todayAuditTitle"
          :cardBodyContent="todayAuditCount"
          :titleIcon="tootltipIcon"
          :titleIconColor="tootltipIconColor"
          :titleIconTooltip="todayAuditTooltip"
        />
        <CardVue
          :cardTitle="currentWeekAuditTitle"
          :cardBodyContent="currentWeekAuditCount"
          :titleIcon="tootltipIcon"
          :titleIconColor="tootltipIconColor"
          :titleIconTooltip="currentWeekAuditTooltip"
        />
        <CardVue
          :cardTitle="currentMonthAuditTitle"
          :cardBodyContent="currentMonthAuditCount"
          :titleIcon="tootltipIcon"
          :titleIconColor="tootltipIconColor"
          :titleIconTooltip="currentMonthAuditTooltip"
        />
        <CardVue
          :cardTitle="currentYearAuditTitle"
          :cardBodyContent="currentYearAuditCount"
          :titleIcon="tootltipIcon"
          :titleIconColor="tootltipIconColor"
          :titleIconTooltip="currentYearAuditTooltip"
        />
        <CardVue
          :cardTitle="allTimeAuditTitle"
          :cardBodyContent="allTimeAuditCount"
          :titleIcon="tootltipIcon"
          :titleIconColor="tootltipIconColor"
          :titleIconTooltip="allTimeAuditTooltip"
        />
      </b-card-group>
    </div>
  </div>

  <div v-if="loadedData">
    <div class="row ms-3 pt-1 card-deck me-2">
      <!-- Audit Trend -->
      <div class="w-auto px-0">
        <div class="pt-5 page-title">
          <h5 class="text-nowrap text-start">Audit Trend</h5>
        </div>

        <b-card-group deck>
          <CardVue
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
      <div class="w-auto px-0">
        <div class="pt-5 page-title">
          <h5 class="text-nowrap text-start">Audit Rank</h5>
        </div>

        <b-card-group deck>
          <CardVue
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
</template>
<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import CardVue, { type CardIcon } from '@/components/Common/CardVue.vue';
import DateUtils from '@/utils/date-utils';
import MetricsService from '@/services/metrics-service';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import { ref, type Ref } from 'vue';
import type { AxiosResponse } from 'axios';
import type { PersonalAuditMetrics, Swr } from '@/services/shema-to-types';

const loadedData = ref(false);

const lastWeekAuditCount = ref(0);

const todayAuditTitle = ref('Today');
const todayAuditCount = ref(0);
const todayAuditTooltip = ref('Total number of findings you triaged today');

const currentWeekAuditTitle = ref('Current Week');
const currentWeekAuditCount = ref(0);
const currentWeekAuditTooltip = ref('Total number of findings you triaged this week');

const currentMonthAuditTitle = ref(`${DateUtils.getCurrentMonth()}-${DateUtils.getCurrentYear()}`);
const currentMonthAuditCount = ref(0);
const currentMonthAuditTooltip = ref('Total number of findings you triaged this month');

const currentYearAuditTitle = ref(`Year-${DateUtils.getCurrentYear()}`);
const currentYearAuditCount = ref(0);
const currentYearAuditTooltip = ref('Total number of findings you triaged this year');

const allTimeAuditTitle = ref('All Time');
const allTimeAuditCount = ref(0);
const allTimeAuditTooltip = ref('Total number of findings you triaged till date');

const currentWeekAuditTrendTitle = ref('Current Week');
const currentWeekAuditTrendPercentageCount = ref('0%');
const currentWeekAuditTrendIcon = ref(undefined) as Ref<CardIcon | undefined>;
const currentWeekAuditTrendIconColor = ref(undefined) as Ref<string | undefined>;
const currentWeekAuditTrendContentColor = ref(undefined) as Ref<string | undefined>;
const currentWeekAuditTrendTooltip = ref('Your audit trend this week in comparison to last week');

const weeklyRankTitle = ref('Current Week');
const weeklyRankValue = ref(0) as Ref<string | number>;
const weeklyRankLabel = ref(undefined) as Ref<string | undefined>;
const weeklyRankIcon = ref(undefined) as Ref<CardIcon | undefined>;
const weeklyRankIconColor = ref(undefined) as Ref<string | undefined>;
const weeklyRankContentColor = ref(undefined) as Ref<string | undefined>;
const weeklyRankTooltip = ref('Your rank based on number of findings you triaged in current week');

const tootltipIcon = ref('info-circle') as Ref<CardIcon>;
const tootltipIconColor = ref('#948C8C');

function isDecimal(num: number): boolean {
  return num % 1 !== 0;
}

function formatPercentageChange(percentage: number): string {
  return isDecimal(percentage) ? percentage.toFixed(2) : percentage.toLocaleString();
}

function formatWeeklyRankLabel(rank: number): string {
  return rank ? convertToRank(rank) : 'No Activity';
}

function calculateAuditTrendInPercentage(): string {
  let percentageChange: number = 0;
  if (!currentWeekAuditCount.value && !lastWeekAuditCount.value) {
    percentageChange = 0;
  } else if (!lastWeekAuditCount.value && currentWeekAuditCount.value) {
    percentageChange = 100;
  } else {
    percentageChange =
      ((currentWeekAuditCount.value - lastWeekAuditCount.value) / lastWeekAuditCount.value) * 100;
  }
  const percentageChangeString = formatPercentageChange(percentageChange);

  if (parseInt(percentageChangeString) < 0) {
    currentWeekAuditTrendIcon.value = 'arrow-down';
    currentWeekAuditTrendIconColor.value = 'red';
    currentWeekAuditTrendContentColor.value = 'red';
  } else if (parseInt(percentageChangeString) > 0) {
    currentWeekAuditTrendIcon.value = 'arrow-up';
    currentWeekAuditTrendIconColor.value = 'green';
    currentWeekAuditTrendContentColor.value = 'green';
  }
  return `${percentageChangeString}%`;
}

function setIconsForAuditRank(rank: number) {
  const mapRankAttr: { icon: CardIcon; color: string }[] = [
    {
      // 0
      icon: 'thumbs-down',
      color: 'red',
    },
    {
      // 1
      icon: 'trophy',
      color: '#FFC107',
    },
    {
      // 2
      icon: 'medal',
      color: '#B87333',
    },
    {
      // 3
      icon: 'award',
      color: '#00BFFF',
    },
  ];
  if (rank < mapRankAttr.length) {
    weeklyRankIcon.value = mapRankAttr[rank].icon;
    weeklyRankIconColor.value = mapRankAttr[rank].color;
    weeklyRankContentColor.value = mapRankAttr[rank].color;
  }
  if (rank === 0) {
    weeklyRankValue.value = 'No Activity';
  }
}

function convertToRank(rank: number) {
  return rank.toString() + getRankSuffix(rank);
}

function getRankSuffix(rank: number): string {
  if ([11, 12, 13].includes(rank)) {
    return 'th';
  }
  switch (rank % 10) {
    case 1:
      return 'st';
    case 2:
      return 'nd';
    case 3:
      return 'rd';
    default:
      return 'th';
  }
}

MetricsService.getPersonalAuditMetrics()
  .then((response: AxiosResponse<PersonalAuditMetrics>) => {
    todayAuditCount.value = response.data.today ?? 0;
    currentWeekAuditCount.value = response.data.current_week ?? 0;
    lastWeekAuditCount.value = response.data.last_week ?? 0;
    currentMonthAuditCount.value = response.data.current_month ?? 0;
    currentYearAuditCount.value = response.data.current_year ?? 0;
    allTimeAuditCount.value = response.data.forever ?? 0;
    weeklyRankValue.value = response.data.rank_current_week ?? 0;
    weeklyRankLabel.value = formatWeeklyRankLabel(response.data.rank_current_week ?? 0);

    currentWeekAuditTrendPercentageCount.value = calculateAuditTrendInPercentage();
    setIconsForAuditRank(weeklyRankValue.value);

    loadedData.value = true;
  })
  .catch((error: Swr) => {
    AxiosConfig.handleError(error);
  });
</script>
