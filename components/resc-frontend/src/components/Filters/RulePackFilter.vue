<template>
  <div>
    <b-form-group class="label-title text-left" label="RulePack" label-for="rule-pack-filter">
      <multiselect
        v-model="selectedVersions"
        :options="rulePackVersions"
        :multiple="true"
        :show-labels="true"
        :close-on-select="true"
        :clear-on-select="false"
        :searchable="true"
        :preserve-search="true"
        :select-label="'Select'"
        :deselect-label="'Remove'"
        placeholder="Select RulePack"
        label="label"
        track-by="id"
        :preselect-first="false"
        @input="onRulePackVersionFilterChange"
      >
        <span slot="noResult">No RulePack found</span>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script>
import Multiselect from 'vue-multiselect';
import Store from '@/store/index.js';

export default {
  name: 'RulePackFilter',
  props: {
    selectedRulePackVersionsList: {
      type: Array,
      required: false,
      default: () => [],
    },
    rulePackVersions: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  data() {
    return {
      selectedVersions: [],
      initialized: false,
    };
  },
  methods: {
    isRedirectedFromRuleMetricsPage() {
      const sourceRoute = Store.getters.sourceRoute;
      const destinationRoute = Store.getters.destinationRoute;
      return sourceRoute === '/metrics/rule-metrics' && destinationRoute === '/rule-analysis'
        ? true
        : false;
    },
    onRulePackVersionFilterChange() {
      if (this.selectedVersions.length > 0) {
        const rulePackVersionValues = [];
        for (const rulePackVersion of this.selectedVersions) {
          const version = rulePackVersion.label.split(' ');
          rulePackVersionValues.push(version.length > 0 ? version[0] : rulePackVersion.label);
        }
        this.$emit('on-rule-pack-version-change', rulePackVersionValues);
      } else {
        this.$emit('on-rule-pack-version-change', null);
      }
    },
  },
  components: {
    Multiselect,
  },
  updated() {
    if (
      !this.initialized &&
      this.selectedRulePackVersionsList.length > 0 &&
      this.selectedVersions.length < 1
    ) {
      this.initialized = true;
      if (this.isRedirectedFromRuleMetricsPage()) {
        // Get selected rule pack version from rule metrics screen
        this.selectedVersions = this.selectedRulePackVersionsList; // To be fixed
      } else {
        // Select the latest version of rule pack by default
        this.selectedVersions = this.selectedRulePackVersionsList;
      }
      this.$emit('on-latest-rule-pack-version-selection', this.selectedVersions);
    }
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
