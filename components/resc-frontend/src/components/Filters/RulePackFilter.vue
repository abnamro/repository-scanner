<template>
  <div>
    <b-form-group class="label-title text-start" label="RulePack" label-for="rule-pack-filter">
      <multiselect
        v-model="selectedRulePack"
        :options="props.rulePackOptions"
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
        @update:modelValue="onRulePackVersionFilterChange"
      >
        <template v-slot:option="proposition">
          <div>
            <span>{{ proposition.option.version }}</span
            ><span v-if="proposition.option.active"> (active)</span>
          </div>
        </template>
        <template v-slot:noResult><span>No RulePack found</span></template>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script setup lang="ts">
import Multiselect from 'vue-multiselect';
import { useAuthUserStore } from '@/store/index';
import { onUpdated, ref } from 'vue';
import type { RulePackRead } from '@/services/shema-to-types';

type Props = {
  rulePackOptions?: RulePackRead[];
  rulePackSelected?: RulePackRead[]; // For testing.
  rulePackPreSelected?: RulePackRead[];
};

const props = withDefaults(defineProps<Props>(), {
  rulePackOptions: () => [],
  rulePackSelected: () => [],
  rulePackPreSelected: () => [],
});

const selectedRulePack = ref(props.rulePackSelected);
const initialized = ref(false);

type LabelForVersion = {
  version: string;
  active: boolean;
};
function customLabelForVersions({ version, active }: LabelForVersion) {
  return active ? `${version} (active)` : version;
}

function isRedirectedFromRuleMetricsPage() {
  const store = useAuthUserStore();
  const sourceRoute = store.sourceRoute;
  const destinationRoute = store.destinationRoute;
  return sourceRoute === '/metrics/rule-metrics' &&
    destinationRoute === '/rule-analysis' &&
    store.previousRouteState
    ? true
    : false;
}

const emit = defineEmits([
  'on-rule-pack-version-change',
  'set-rule-pack-versions-on-rule-pack-filter',
]);

function onRulePackVersionFilterChange() {
  if (selectedRulePack.value.length > 0) {
    emit('on-rule-pack-version-change', selectedRulePack.value);
  } else {
    emit('on-rule-pack-version-change', []);
  }
}

function update() {
  if (
    !initialized.value &&
    props.rulePackPreSelected.length > 0 &&
    selectedRulePack.value.length < 1
  ) {
    initialized.value = true;
    if (isRedirectedFromRuleMetricsPage()) {
      // Get selected rule pack versions from Rule metrics screen and set it on Rule analyis page
      for (const obj of props.rulePackPreSelected) {
        selectedRulePack.value.push(obj);
      }
    } else {
      // Select the latest version of rule pack version on Rule analysis page filter
      selectedRulePack.value = props.rulePackPreSelected;
    }
    emit('set-rule-pack-versions-on-rule-pack-filter', selectedRulePack.value);
  }
}
onUpdated(() => update());
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
