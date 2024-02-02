<template>
  <div>
    <b-form-group class="label-title text-start" label="Repository" label-for="repository-filter">
      <multiselect
        v-model="selectedRepository"
        :options="props.repositoryOptions"
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
        @update:modelValue="onRepositoryFilterChange"
      >
        <template v-slot:noResult><span>No repository found</span></template>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import Multiselect from 'vue-multiselect';

type Props = {
  repositoryOptions: string[];
  repositorySelected?: string;
};

const props = defineProps<Props>();

const selectedRepository = ref(props.repositorySelected);

const emit = defineEmits(['on-repository-change']);

function onRepositoryFilterChange() {
  emit('on-repository-change', selectedRepository.value ?? undefined);
}
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
