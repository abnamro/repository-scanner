<template>
  <div>
    <b-form-group class="label-title text-left" label="RulePack" label-for="rule-pack-filter">
      <multiselect
        v-model="selectedVersions"
        :options="rulePackVersions"
        :custom-label="customLabelForVersions"
        :multiple="true"
        :show-labels="false"
        :close-on-select="true"
        :clear-on-select="false"
        :searchable="true"
        :preserve-search="true"
        :select-label="'Select'"
        :deselect-label="'Remove'"
        placeholder="Select RulePack"
        label="version"
        track-by="version"
        :preselect-first="false"
        @input="onRulePackVersionFilterChange"
      >
        <template slot="option" slot-scope="props">
          <div>
            <span>{{ props.option.version }}</span
            ><span v-if="props.option.active"> (active)</span>
          </div>
        </template>
        <span slot="noResult">No RulePack found</span>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script>
import Multiselect from 'vue-multiselect';
import { useAuthUserStore } from '@/store/index.js';

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
    customLabelForVersions({ version, active }) {
      return active ? `${version} (active)` : version;
    },
    isRedirectedFromRuleMetricsPage() {
      const store = useAuthUserStore();
      const sourceRoute = store.sourceRoute;
      const destinationRoute = store.destinationRoute;
      return sourceRoute === '/metrics/rule-metrics' &&
        destinationRoute === '/rule-analysis' &&
        store.previousRouteState
        ? true
        : false;
    },
    onRulePackVersionFilterChange() {
      if (this.selectedVersions.length > 0) {
        this.$emit('on-rule-pack-version-change', this.selectedVersions);
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
        // Get selected rule pack versions from Rule metrics screen and set it on Rule analyis page
        for (const obj of this.selectedRulePackVersionsList) {
          this.selectedVersions.push(obj);
        }
      } else {
        // Select the latest version of rule pack version on Rule analysis page filter
        this.selectedVersions = this.selectedRulePackVersionsList;
      }
      this.$emit('set-rule-pack-versions-on-rule-pack-filter', this.selectedVersions);
    }
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
