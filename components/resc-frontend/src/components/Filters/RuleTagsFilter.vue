<template>
  <div>
    <b-form-group class="label-title text-start" label="Tags" label-for="rule-tags-filter">
      <multiselect
        v-model="selectedRuleTags"
        :options="props.ruleTagsOptions"
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
        @update:modelValue="onRuleTagFilterChange"
      >
        <template v-slot:noResult><span>No tag found</span></template>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script setup lang="ts">
import { ref, watch } from 'vue';
import Multiselect from 'vue-multiselect';

type Props = {
  ruleTagsOptions: string[];
  ruleTagsSelected?: string[];
};

const props = withDefaults(defineProps<Props>(), { ruleTagsSelected: () => [] });
const selectedRuleTags = ref(props.ruleTagsSelected);

const emit = defineEmits(['on-rule-tags-change']);

function onRuleTagFilterChange() {
  if (selectedRuleTags.value.length > 0) {
    emit('on-rule-tags-change', selectedRuleTags.value);
  } else {
    emit('on-rule-tags-change', []);
  }
}

function resetRuleTagsFilterSelection() {
  selectedRuleTags.value = props.ruleTagsSelected;
}

// Double check if I work.
watch(
  () => props.ruleTagsSelected,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  (newValue, _second) => {
    selectedRuleTags.value = newValue;
  }
);

defineExpose({ resetRuleTagsFilterSelection });
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
