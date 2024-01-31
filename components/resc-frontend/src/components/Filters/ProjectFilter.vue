<template>
  <div>
    <b-form-group class="label-title text-start" label="Project" label-for="project-filter">
      <multiselect
        v-model="selectedProject"
        :options="props.projectOptions"
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
        @update:modelValue="onProjectFilterChange"
      >
        <template v-slot:noResult><span>No project found</span></template>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import Multiselect from 'vue-multiselect';

type Props = {
  projectOptions: string[];
  projectSelected?: string;
};

const props = defineProps<Props>();

const selectedProject = ref(props.projectSelected);

const emit = defineEmits(['on-project-change']);

function onProjectFilterChange() {
  emit('on-project-change', selectedProject.value ?? undefined);
}
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
