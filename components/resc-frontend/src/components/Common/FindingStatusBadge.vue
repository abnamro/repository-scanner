<template>
  <div>
    <b-badge v-if="status == 'NOT_ANALYZED'" variant="secondary">Not Analyzed</b-badge>
    <b-badge v-if="status == 'UNDER_REVIEW'" variant="info">Under Review</b-badge>
    <b-badge v-if="status == 'CLARIFICATION_REQUIRED'" variant="warning"
      >Clarification Required</b-badge
    >
    <b-badge v-if="status == 'TRUE_POSITIVE'" variant="danger">True Positive</b-badge>
    <b-badge v-if="status == 'FALSE_POSITIVE'" variant="success">False Positive</b-badge>
  </div>
</template>
<script>
export default {
  name: 'FindingStatusBadge',
  props: {
    status: {
      type: String,
      required: true,
    },
  },
};
</script>
