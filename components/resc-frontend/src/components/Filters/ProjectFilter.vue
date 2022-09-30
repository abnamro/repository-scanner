<template>
  <div>
    <b-form-group class="label-title text-left" label="Project" label-for="project-filter">
      <multiselect
        v-model="selectedProject"
        :options="projectOptions"
        :multiple="false"
        :show-labels="true"
        :close-on-select="true"
        :clear-on-select="false"
        :searchable="true"
        :preserve-search="true"
        :select-label="'Select'"
        :deselect-label="'Remove'"
        placeholder="Select Project"
        :preselect-first="false"
        @input="onProjectFilterChange"
      >
        <span slot="noResult">No project found</span>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script>
import Multiselect from 'vue-multiselect';

export default {
  name: 'ProjectFilter',
  props: {
    projectOptions: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  data() {
    return {
      selectedProject: null,
    };
  },
  methods: {
    onProjectFilterChange() {
      this.$emit('on-project-change', this.selectedProject);
    },
  },
  components: {
    Multiselect,
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
