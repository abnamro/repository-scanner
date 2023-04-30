<template>
  <div>
    <div class="row">
      <!--Rule Filter -->
      <div class="col-md-4 ml-3">
        <RuleFilter
          :options="rules"
          :requestedRuleFilterValue="selectedRule"
          @on-rule-change="onRuleChange"
        />
      </div>
      <!-- Status Filter -->
      <div class="col-md-4">
        <FindingStatusFilter @on-findings-status-change="onFindingsStatusChange" />
      </div>
      <div class="col-md-2 mt-1 ml-1 pt-1">
        <b-button variant="prime" class="mt-4" size="sm" v-b-toggle:advance-search-collapse>
          Advanced Search
        </b-button>
      </div>
    </div>

    <div class="ml-3 mt-2 mb-1">
      <b-collapse id="advance-search-collapse">
        <div class="row">
          <!-- VCS Filter -->
          <div class="col-md-3">
            <VcsProviderFilter @on-vcs-change="onVcsProviderChange" />
          </div>
          <!--Project Filter -->
          <div class="col-md-3">
            <ProjectFilter :projectOptions="projectOptions" @on-project-change="onProjectChange" />
          </div>
          <!--Repository Filter -->
          <div class="col-md-4">
            <RepositoryFilter
              :repositoryOptions="repositoryOptions"
              @on-repository-change="onRepositoryChange"
            />
          </div>
        </div>

        <div class="row">
          <!-- Start Date Filter -->
          <div class="col-md-3">
            <b-form-group class="label-title text-left" label="From Date" label-for="start-date">
              <b-form-datepicker
                id="start-date"
                size="md"
                placeholder="Enter Scan Start Date"
                selected-variant="success"
                reset-button
                v-model="startDate"
                :max="todaysDate"
                @input="onStartDateChange"
              ></b-form-datepicker>
            </b-form-group>
          </div>

          <!-- End Date Filter -->
          <div class="col-md-3">
            <b-form-group class="label-title text-left" label="To Date" label-for="end-date">
              <b-form-datepicker
                id="end-date"
                size="md"
                placeholder="Enter Scan End Date"
                selected-variant="success"
                reset-button
                v-model="endDate"
                :min="minEndDate"
                :max="todaysDate"
                :disabled="endDateDisabled"
                @input="onEndDateChange"
              ></b-form-datepicker>
            </b-form-group>
          </div>

          <div class="col-md-4">
            <RulePackFilter
              :selectedRulePackVersionsList="selectedRulePackVersionsList"
              :rulePackVersions="rulePackVersions"
              @on-rule-pack-version-change="onRulePackVersionChange"
              @set-rule-pack-versions-on-rule-pack-filter="setRulePackVersionsOnRulePackFilter"
            />
          </div>
        </div>
      </b-collapse>
    </div>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import FindingStatusFilter from '@/components/Filters/FindingStatusFilter.vue';
import ProjectFilter from '@/components/Filters/ProjectFilter.vue';
import RepositoryFilter from '@/components/Filters/RepositoryFilter.vue';
import RuleFilter from '@/components/Filters/RuleFilter.vue';
import RuleService from '@/services/rule-service';
import Store from '@/store/index.js';
import VcsProviderFilter from '@/components/Filters/VcsProviderFilter.vue';
import RulePackFilter from '@/components/Filters/RulePackFilter.vue';

export default {
  name: 'RuleAnalysisFilter',
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
      rules: [],
      startDate: '',
      endDate: '',
      selectedVcsProvider: null,
      selectedStatus: null,
      selectedProject: null,
      selectedRepository: null,
      selectedBranch: null,
      selectedRule: null,
      selectedRulePackVersions: [],
    };
  },
  computed: {
    todaysDate() {
      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      return new Date(today);
    },
    minEndDate() {
      return this.startDate;
    },
    endDateDisabled() {
      return this.startDate ? false : true;
    },
    searchButtonDisabled() {
      return !this.selectedProject && !this.selectedRepository && !this.selectedBranch;
    },
  },
  methods: {
    onStartDateChange() {
      this.fetchAllDetectedRules();
      this.handleFilterChange();
    },

    onEndDateChange() {
      this.fetchAllDetectedRules();
      this.handleFilterChange();
    },

    onVcsProviderChange(vcsProvider) {
      this.selectedVcsProvider = vcsProvider;
      this.fetchAllDetectedRules();
      this.handleFilterChange();
    },

    onProjectChange(project) {
      this.selectedProject = project;
      this.fetchAllDetectedRules();
      this.handleFilterChange();
    },

    onRepositoryChange(repository) {
      this.selectedRepository = repository;
      this.fetchAllDetectedRules();
      this.handleFilterChange();
    },

    onFindingsStatusChange(status) {
      this.selectedStatus = status;
      this.fetchAllDetectedRules();
      this.handleFilterChange();
    },

    onRuleChange(rule) {
      this.selectedRule = rule;
      this.handleFilterChange();
    },

    onRulePackVersionChange(rulePackVersions) {
      this.selectedRulePackVersions = rulePackVersions;
      this.fetchAllDetectedRules();
      this.handleFilterChange();
    },

    setRulePackVersionsOnRulePackFilter(rulePackVersions) {
      this.selectedRulePackVersions = rulePackVersions;
      this.fetchAllDetectedRules();
    },

    handleFilterChange() {
      // Refresh table data in Rule Analysis page
      const filterObj = {};
      const rulePackVersions = [];
      if (this.selectedRulePackVersions) {
        for (const obj of this.selectedRulePackVersions) {
          rulePackVersions.push(obj.version);
        }
      }

      filterObj.startDate = this.startDate;
      filterObj.endDate = this.endDate;
      filterObj.vcsProvider = this.selectedVcsProvider;
      filterObj.status = this.selectedStatus;
      filterObj.project = this.selectedProject;
      filterObj.repository = this.selectedRepository;
      filterObj.branch = this.selectedBranch;
      filterObj.rule = this.selectedRule;
      filterObj.rulePackVersions = rulePackVersions;
      this.$emit('on-filter-change', filterObj);
    },
    fetchAllDetectedRules() {
      const rulePackVersions = [];
      if (this.selectedRulePackVersions) {
        for (const obj of this.selectedRulePackVersions) {
          rulePackVersions.push(obj.version);
        }
      }
      RuleService.getAllDetectedRules(
        this.selectedStatus,
        this.selectedVcsProvider,
        this.selectedProject,
        this.selectedRepository,
        this.startDate,
        this.endDate,
        rulePackVersions
      )
        .then((response) => {
          this.rules = response.data;
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    applyRuleFilterInRuleAnalysisPage() {
      const selectedRules = [];
      const selectedVersions = [];
      if (Store.getters.previousRouteState) {
        selectedRules.push(Store.getters.previousRouteState.ruleName);
        if (Store.getters.previousRouteState.rulePackVersions) {
          for (const obj of Store.getters.previousRouteState.rulePackVersions) {
            selectedVersions.push(obj.version);
          }
        }
      }
      const sourceRoute = Store.getters.sourceRoute;
      const destinationRoute = Store.getters.destinationRoute;

      if (
        selectedRules.length > 0 &&
        sourceRoute === '/metrics/rule-metrics' &&
        destinationRoute === '/rule-analysis'
      ) {
        const filterObj = {};
        filterObj.startDate = this.startDate;
        filterObj.endDate = this.endDate;
        filterObj.vcsProvider = this.selectedVcsProvider;
        filterObj.status = this.selectedStatus;
        filterObj.project = this.selectedProject;
        filterObj.repository = this.selectedRepository;
        filterObj.branch = this.selectedBranch;
        filterObj.rule = selectedRules;
        filterObj.rulePackVersions = selectedVersions;

        //Populate rule analysis list based on rule filter
        this.$emit('on-filter-change', filterObj);

        //Set rule fiter dropdown selected value
        this.selectedRule = selectedRules;
      } else {
        this.selectedRule = [];
      }
    },
  },
  created() {
    this.applyRuleFilterInRuleAnalysisPage();
  },
  components: {
    FindingStatusFilter,
    ProjectFilter,
    RepositoryFilter,
    RuleFilter,
    VcsProviderFilter,
    RulePackFilter,
  },
};
</script>
