<template>
  <div>
    <div class="row">
      <!--VCS Filter -->
      <div class="col-md-3">
        <VcsProviderFilter @on-vcs-change="onVcsProviderChange" />
      </div>

      <!--Project Filter -->
      <div class="col-md-4">
        <ProjectFilter :projectOptions="projectOptions" @on-project-change="onProjectChange" />
      </div>

      <!--Repository Search Filter -->
      <div class="col-md-4">
        <RepositoryFilter
          :repositoryOptions="repositoryOptions"
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

<script>
import ProjectFilter from '@/components/Filters/ProjectFilter.vue';
import RepositoryFilter from '@/components/Filters/RepositoryFilter.vue';
import VcsProviderFilter from '@/components/Filters/VcsProviderFilter.vue';

export default {
  name: 'RepositoriesPageFilter',
  props: {
    projectOptions: {
      type: Array,
      required: false,
      default: () => [],
    },
    repositoryOptions: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  data() {
    return {
      selectedVcsProvider: null,
      selectedProject: null,
      selectedRepository: null,
      includeZeroFindingRepos: false,
    };
  },
  methods: {
    onProjectChange(project) {
      this.selectedProject = project;
      this.handleFilterChange();
    },
    onRepositoryChange(repository) {
      this.selectedRepository = repository;
      this.handleFilterChange();
    },
    onVcsProviderChange(vcsProvider) {
      this.selectedVcsProvider = vcsProvider;
      this.handleFilterChange();
    },
    toggleIncludeZeroFindingRepos() {
      this.handleFilterChange();
    },
    handleFilterChange() {
      // Refresh table data in Repositories page
      this.$emit(
        'on-filter-change',
        this.selectedVcsProvider,
        this.selectedProject,
        this.selectedRepository,
        this.includeZeroFindingRepos
      );
    },
  },
  components: {
    ProjectFilter,
    RepositoryFilter,
    VcsProviderFilter,
  },
};
</script>
