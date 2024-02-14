<template>
  <div>
    <b-progress class="mt-2" :max="props.totalCount" height="0.8rem" show-value>
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent('True Positive', props.truePositive)"
        :value="props.truePositive"
        variant="danger"
      >
        <div>
          <small>
            <strong>{{ showFindingsInPercentage(props.truePositive) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent('False Positive', props.falsePositive)"
        :value="props.falsePositive"
        variant="success"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(props.falsePositive) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <b-progress-bar
        v-b-popover.hover.bottom="
          getPopOverContent('Clarification Required', props.clarificationRequired)
        "
        :value="props.clarificationRequired"
        variant="warning"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(props.clarificationRequired) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent('Under Review', props.underReview)"
        :value="props.underReview"
        variant="info"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(props.underReview) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <!-- @vue-ignore -->
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent('Not Analyzed', props.notAnalyzed)"
        :value="props.notAnalyzed"
        variant="not-analyzed"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(props.notAnalyzed) }}</strong></small
          >
        </div>
      </b-progress-bar>
    </b-progress>
  </div>
</template>
<script setup lang="ts">
type Props = {
  truePositive: number;
  falsePositive: number;
  notAnalyzed: number;
  underReview: number;
  clarificationRequired: number;
  totalCount: number;
};
const props = defineProps<Props>();

const percent = 100;
function showFindingsInPercentage(count: number) {
  return String(Math.round((count / props.totalCount) * percent));
}

function getPopOverContent(title: string, count: number) {
  const percentage = showFindingsInPercentage(count);
  return `${title}<hr>count: ${count}, percentage: ${percentage}%`;
}
</script>
