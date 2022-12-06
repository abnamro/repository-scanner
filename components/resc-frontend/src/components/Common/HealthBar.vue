<template>
  <div>
    <b-progress class="mt-2" :max="total" height="0.8rem" show-value>
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent(truePositiveCount)"
        title="True Positive"
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
        v-b-popover.hover.bottom="getPopOverContent(falsePositiveCount)"
        title="False Positive"
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
        v-b-popover.hover.bottom="getPopOverContent(clarificationRequiredCount)"
        title="Clarification Required"
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
        v-b-popover.hover.bottom="getPopOverContent(underReviewCount)"
        title="Under Review"
        :value="underReviewCount"
        variant="info"
      >
        <div>
          <small
            ><strong>{{ showFindingsInPercentage(underReviewCount) }}</strong></small
          >
        </div>
      </b-progress-bar>
      <b-progress-bar
        v-b-popover.hover.bottom="getPopOverContent(notAnalyzedCount)"
        title="Not Analyzed"
        :value="notAnalyzedCount"
        variant="secondary"
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
<script>
export default {
  name: 'HealthBar',
  props: {
    truePositive: {
      type: Number,
      required: true,
    },
    falsePositive: {
      type: Number,
      required: true,
    },
    notAnalyzed: {
      type: Number,
      required: true,
    },
    underReview: {
      type: Number,
      required: true,
    },
    clarificationRequired: {
      type: Number,
      required: true,
    },
    totalCount: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      truePositiveCount: this.truePositive,
      falsePositiveCount: this.falsePositive,
      notAnalyzedCount: this.notAnalyzed,
      underReviewCount: this.underReview,
      clarificationRequiredCount: this.clarificationRequired,
      total: this.totalCount,
    };
  },
  methods: {
    showFindingsInPercentage(count) {
      return String(Math.round((count / this.totalCount) * 100));
    },
    getPopOverContent(count) {
      const percentage = this.showFindingsInPercentage(count);
      return `count: ${count}, percentage: ${percentage}%`;
    },
  },
};
</script>
