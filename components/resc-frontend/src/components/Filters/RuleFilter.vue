<template>
  <div>
    <b-form-group class="label-title text-start" label="Rule" label-for="rule-filter">
      <multiselect
        v-model="selectedRules"
        :options="props.rulesOptions"
        :multiple="true"
        :show-labels="true"
        :close-on-select="true"
        :clear-on-select="false"
        :searchable="true"
        :preserve-search="true"
        :select-label="'Select'"
        :deselect-label="'Remove'"
        placeholder="Select Rule"
        :preselect-first="false"
        @update:modelValue="onRuleFilterChange"
      >
        <template v-slot:noResult><span>No rule found</span></template>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue';
import Multiselect from 'vue-multiselect';

type Props = {
  rulesOptions: string[];
  rulesSelected?: string[];
};

const props = withDefaults(defineProps<Props>(), { rulesSelected: () => [] });

const selectedRules = ref(props.rulesSelected);
const emit = defineEmits(['on-rule-change']);

function onRuleFilterChange() {
  if (selectedRules.value.length > 0) {
    emit('on-rule-change', selectedRules.value);
  } else {
    emit('on-rule-change', []);
  }
}

function resetRuleFilterSelection() {
  selectedRules.value = props.rulesSelected;
}

// Double check if I work.
watch(
  () => props.rulesSelected,
  (newValue, _second) => {
    selectedRules.value = newValue;
  }
);

// We probably need to expose this.
defineExpose({ resetRuleFilterSelection });
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
