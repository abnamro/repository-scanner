<template>
  <div>
    <b-form-group class="label-title text-left" label="Tags" label-for="rule-tags-filter">
      <multiselect
        v-model="selectedRuleTags"
        :options="options"
        :multiple="true"
        :show-labels="true"
        :close-on-select="true"
        :clear-on-select="false"
        :searchable="true"
        :preserve-search="true"
        :select-label="'Select'"
        :deselect-label="'Remove'"
        placeholder="Select Tag"
        :preselect-first="false"
        @input="onRuleTagFilterChange"
      >
        <span slot="noResult">No tag found</span>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script>
import Multiselect from 'vue-multiselect';

export default {
  name: 'RuleTagsFilter',
  props: {
    options: {
      type: Array,
      required: true,
    },
    requestedRuleTagsFilterValue: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  data() {
    return {
      selectedRuleTags: this.requestedRuleTagsFilterValue,
    };
  },
  methods: {
    onRuleTagFilterChange() {
      if (this.selectedRuleTags.length > 0) {
        this.$emit('on-rule-tags-change', this.selectedRuleTags);
      } else {
        this.$emit('on-rule-tags-change', null);
      }
    },
    resetRuleTagsFilterSelection() {
      this.selectedRuleTags = this.requestedRuleTagsFilterValue;
    },
  },
  watch: {
    requestedRuleTagsFilterValue(newValue) {
      this.selectedRuleTags = newValue;
    },
  },
  components: {
    Multiselect,
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
