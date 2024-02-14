<template>
  <div>
    <div class="row">
      <!--VCS Filter -->
      <div class="col-md-3">
        <VcsProviderFilter @on-vcs-change="onVcsProviderChange" />
      </div>

      <!--Project Filter -->
      <div class="col-md-4">
        <ProjectFilter
          :projectOptions="props.projectOptions"
          @on-project-change="onProjectChange"
        />
      </div>

      <!--Repository Search Filter -->
      <div class="col-md-4">
        <RepositoryFilter
          :repositoryOptions="props.repositoryOptions"
          @on-repository-change="onRepositoryChange"
        />
      </div>
    </div>

    <!-- Include zero finding repos -->
    <div class="row">
      <div class="col-md-2">
        <b-form-checkbox
          v-model="includeZeroFindingRepos"
          name="check-button"
          switch
          @change="toggleIncludeZeroFindingRepos"
        >
          <small class="text-nowrap">Display repositories with 0 findings</small>
        </b-form-checkbox>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ProjectFilter from '@/components/Filters/ProjectFilter.vue';
import RepositoryFilter from '@/components/Filters/RepositoryFilter.vue';
import VcsProviderFilter from '@/components/Filters/VcsProviderFilter.vue';
import type { VCSProviders } from '@/services/shema-to-types';
import { ref } from 'vue';

type Props = {
  projectOptions: string[];
  projectSelected?: string;
  repositoryOptions: string[];
  repositorySelected?: string;
  vcsProviderSelected?: VCSProviders[];
};

const props = withDefaults(defineProps<Props>(), {
  vcsProviderSelected: () => [],
});

const selectedVcsProvider = ref(props.vcsProviderSelected);
const selectedProject = ref(props.projectSelected);
const selectedRepository = ref(props.repositorySelected);
const includeZeroFindingRepos = ref(false);

const emit = defineEmits(['on-filter-change']);

function onProjectChange(project: string | undefined) {
  selectedProject.value = project;
  handleFilterChange();
}
function onRepositoryChange(repository: string | undefined) {
  selectedRepository.value = repository;
  handleFilterChange();
}
function onVcsProviderChange(vcsProvider: VCSProviders[]) {
  selectedVcsProvider.value = vcsProvider;
  handleFilterChange();
}
function toggleIncludeZeroFindingRepos() {
  handleFilterChange();
}

function handleFilterChange() {
  // Refresh table data in Repositories page
  emit(
    'on-filter-change',
    selectedVcsProvider.value,
    selectedProject.value,
    selectedRepository.value,
    includeZeroFindingRepos.value,
  );
}
</script>
