<template>
  <div>
    <b-form-group class="label-title text-left" label="VCS Provider" label-for="vcs-filter">
      <multiselect
        v-model="selectedVcsProviderList"
        :options="vcsProviders"
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
        @input="onVcsFilterChange"
      >
        <span slot="noResult">No vcs provider found</span>
      </multiselect>
    </b-form-group>
  </div>
</template>
<script>
import AxiosConfig from '@/configuration/axios-config.js';
import Multiselect from 'vue-multiselect';
import RepositoryService from '@/services/repository-service';

export default {
  name: 'VcsProviderFilter',
  data() {
    return {
      vcsProviders: [],
      selectedVcsProviderList: [],
    };
  },
  methods: {
    onVcsFilterChange() {
      if (this.selectedVcsProviderList.length > 0) {
        const vcsProviderValues = [];
        for (const vcs of this.selectedVcsProviderList) {
          vcsProviderValues.push(vcs.value);
        }
        this.$emit('on-vcs-change', vcsProviderValues);
      } else {
        this.$emit('on-vcs-change', null);
      }
    },
    fetchSupportedVCSProviders() {
      RepositoryService.getVCSProviders()
        .then((response) => {
          this.vcsProviders = [];
          for (const index of response.data.keys()) {
            const vcsJson = {};
            vcsJson['id'] = index;
            vcsJson['value'] = response.data[index];
            if (response.data[index] === 'AZURE_DEVOPS') {
              vcsJson['label'] = 'AZURE DEVOPS';
            } else if (response.data[index] === 'BITBUCKET') {
              vcsJson['label'] = 'BITBUCKET';
            } else if (response.data[index] === 'GITHUB_PUBLIC') {
              vcsJson['label'] = 'GITHUB PUBLIC';
            }
            this.vcsProviders.push(vcsJson);
          }
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
  },
  created() {
    this.fetchSupportedVCSProviders();
  },
  components: {
    Multiselect,
  },
};
</script>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
