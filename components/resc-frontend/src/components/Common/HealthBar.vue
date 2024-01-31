<template>
  <div>
    <b-progress class="mt-2" :max="total" height="0.8rem" show-value>
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent('True Positive', truePositiveCount)"
        :value="truePositiveCount"
        variant="danger"
      >
        <div>
          <small>
            <strong>{{ showFindingsInPercentage(truePositiveCount) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent('False Positive', falsePositiveCount)"
        :value="falsePositiveCount"
        variant="success"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(falsePositiveCount) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <b-progress-bar
        v-b-popover.hover.bottom="
          getPopOverContent('Clarification Required', clarificationRequiredCount)
        "
        :value="clarificationRequiredCount"
        variant="warning"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(clarificationRequiredCount) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent('Under Review', underReviewCount)"
        :value="underReviewCount"
        variant="info"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(underReviewCount) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <!-- @vue-ignore -->
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent('Not Analyzed', notAnalyzedCount)"
        :value="notAnalyzedCount"
        variant="not-analyzed"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(notAnalyzedCount) }}</strong></small
          >
        </div>
      </b-progress-bar>
    </b-progress>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
type Props = {
  truePositive: number;
  falsePositive: number;
  notAnalyzed: number;
  underReview: number;
  clarificationRequired: number;
  totalCount: number;
};
const props = defineProps<Props>();

const truePositiveCount = ref(props.truePositive);
const falsePositiveCount = ref(props.falsePositive);
const notAnalyzedCount = ref(props.notAnalyzed);
const underReviewCount = ref(props.underReview);
const clarificationRequiredCount = ref(props.clarificationRequired);
const total = ref(props.totalCount);

const percent = 100;
function showFindingsInPercentage(count: number) {
  return String(Math.round((count / total.value) * percent));
}

function getPopOverContent(title: string, count: number) {
  const percentage = showFindingsInPercentage(count);
  return `${title}<hr>count: ${count}, percentage: ${percentage}%`;
}
</script>
