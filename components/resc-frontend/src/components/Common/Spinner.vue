<template>
  <b-spinner v-if="active" variant="spinner" class="spinner"></b-spinner>
</template>

<script>
export default {
  name: 'Spinner',
  props: {
    active: Boolean,
  },
};
</script>
