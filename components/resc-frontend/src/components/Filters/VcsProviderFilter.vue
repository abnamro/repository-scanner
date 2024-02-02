<template>
  <div>
    <b-form-group class="label-title text-start" label="VCS Provider" label-for="vcs-filter">
      <multiselect
        v-model="selectedVcsProviders"
        :options="optionsVcsProviders"
        :multiple="true"
        :show-labels="true"
        :close-on-select="true"
        :clear-on-select="false"
        :searchable="true"
        :preserve-search="true"
        :select-label="'Select'"
        :deselect-label="'Remove'"
        placeholder="Select VCS Provider"
        label="label"
        track-by="id"
        :preselect-first="false"
        @update:modelValue="onVcsFilterChange"
      >
        <template v-slot:noResult><span>No vcs provider found</span></template>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import Multiselect from 'vue-multiselect';
import CommonUtils from '@/utils/common-utils';
import RepositoryService from '@/services/repository-service';
import { ref } from 'vue';
import type { VCSProviders } from '@/services/shema-to-types';

type VcsProvider = {
  id: number;
  value: string;
  label: string;
};

type Props = {
  vcsProvidersOptions?: VcsProvider[];
  vcsProvidersSelected?: VcsProvider[];
};

const props = withDefaults(defineProps<Props>(), {
  vcsProvidersOptions: () => [],
  vcsProvidersSelected: () => [],
});

const optionsVcsProviders = ref(props.vcsProvidersOptions);
const selectedVcsProviders = ref(props.vcsProvidersSelected);

const emit = defineEmits(['on-vcs-change']);

function onVcsFilterChange() {
  if (selectedVcsProviders.value.length > 0) {
    const vcsProviderValues = [];
    for (const vcs of selectedVcsProviders.value) {
      vcsProviderValues.push(vcs.value);
    }
    emit('on-vcs-change', vcsProviderValues);
  } else {
    emit('on-vcs-change', []);
  }
}

RepositoryService.getVCSProviders()
  .then((response) => {
    optionsVcsProviders.value = [];
    for (const index of response.data.keys()) {
      const vcsJson: VcsProvider = {
        id: index,
        value: response.data[index],
        label: CommonUtils.formatVcsProvider(response.data[index] as VCSProviders),
      };
      optionsVcsProviders.value.push(vcsJson);
    }
  })
  .catch((error) => {
    AxiosConfig.handleError(error);
  });
</script>
<style src="vue-multiselect/dist/vue-multiselect.css"></style>
