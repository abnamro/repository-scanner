<template>
  <div>
    <b-form-group class="label-title text-left" label="Repository" label-for="repository-filter">
      <multiselect
        v-model="selectedRepository"
        :options="repositoryOptions"
        :multiple="false"
        :show-labels="true"
        :close-on-select="true"
        :clear-on-select="false"
        :searchable="true"
        :preserve-search="true"
        :select-label="'Select'"
        :deselect-label="'Remove'"
        placeholder="Select Repository"
        :preselect-first="false"
        @input="onRepositoryFilterChange"
      >
        <span slot="noResult">No repository found</span>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script>
import Multiselect from 'vue-multiselect';

export default {
  name: 'RepositoryFilter',
  props: {
    repositoryOptions: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  data() {
    return {
      selectedRepository: null,
    };
  },
  methods: {
    onRepositoryFilterChange() {
      this.$emit('on-repository-change', this.selectedRepository);
    },
  },
  components: {
    Multiselect,
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
