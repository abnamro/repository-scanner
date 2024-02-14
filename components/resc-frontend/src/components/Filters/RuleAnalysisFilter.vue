<template>
  <div>
    <div class="row">
      <!--Rule Filter -->
      <div class="col-md-4 ml-3">
        <RuleFilter
          :rulesOptions="optionsRules"
          :rulesSelected="selectedRule"
          @on-rule-change="onRuleChange"
        />
      </div>
      <!-- Status Filter -->
      <div class="col-md-4">
        <FindingStatusFilter @on-findings-status-change="onFindingsStatusChange" />
      </div>
      <div class="col-md-2 mt-1 ml-1 pt-1">
        <b-button variant="primary" class="mt-4" size="sm" v-b-toggle.advance-search-collapse>
          Advanced Search
        </b-button>
      </div>
    </div>

    <div class="ml-3 mt-2 mb-1">
      <b-collapse id="advance-search-collapse">
        <div class="row pt-1">
          <!-- VCS Filter -->
          <div class="col-md-3">
            <VcsProviderFilter @on-vcs-change="onVcsProviderChange" />
          </div>
          <!--Project Filter -->
          <div class="col-md-3">
            <ProjectFilter
              :projectOptions="props.projectOptions"
              @on-project-change="onProjectChange"
            />
          </div>
          <!--Repository Filter -->
          <div class="col-md-4">
            <RepositoryFilter
              :repositoryOptions="props.repositoryOptions"
              @on-repository-change="onRepositoryChange"
            />
          </div>
        </div>

        <div class="row pt-1">
          <!-- Start Date Filter -->
          <!-- <div class="col-md-3">
            <b-form-group class="label-title text-start" label="From Date" label-for="start-date">
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
          </div> -->

          <!-- End Date Filter -->
          <!-- <div class="col-md-3">
            <b-form-group class="label-title text-start" label="To Date" label-for="end-date">
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
          </div> -->

          <div class="col-md-4">
            <RulePackFilter
              :rulePackPreSelected="props.rulePackPreSelected"
              :rulePackOptions="props.rulePackOptions"
              @on-rule-pack-version-change="onRulePackVersionChange"
              @set-rule-pack-versions-on-rule-pack-filter="setRulePackVersionsOnRulePackFilter"
            />
          </div>
          <!-- </div>
        <div class="row"> -->
          <!-- Rule Tags Filter -->
          <div class="col-md-3">
            <RuleTagsFilter
              :ruleTagsOptions="optionsRuleTags"
              :ruleTagsSelected="selectedRuleTags"
              @on-rule-tags-change="onRuleTagsChange"
            />
          </div>
        </div>
      </b-collapse>
    </div>
  </div>
</template>

<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import FindingStatusFilter from '@/components/Filters/FindingStatusFilter.vue';
import ProjectFilter from '@/components/Filters/ProjectFilter.vue';
import RepositoryFilter from '@/components/Filters/RepositoryFilter.vue';
import RuleFilter from '@/components/Filters/RuleFilter.vue';
import RulePackService from '@/services/rule-pack-service';
import RuleService from '@/services/rule-service';
import { useAuthUserStore, type PreviousRouteState } from '@/store/index';
import VcsProviderFilter from '@/components/Filters/VcsProviderFilter.vue';
import RulePackFilter from '@/components/Filters/RulePackFilter.vue';
import RuleTagsFilter from '@/components/Filters/RuleTagsFilter.vue';
import { ref } from 'vue';
import type { FindingStatus, RulePackRead, VCSProviders } from '@/services/shema-to-types';
import type { Ref } from 'vue';

type Props = {
  projectOptions?: string[];
  repositoryOptions?: string[];
  rulePackPreSelected?: RulePackRead[];
  rulePackOptions?: RulePackRead[];
};

const props = withDefaults(defineProps<Props>(), {
  projectOptions: () => [],
  repositoryOptions: () => [],
  rulePackPreSelected: () => [],
  rulePackOptions: () => [],
});

export type RuleAnalysisFilter = {
  startDate: string | undefined;
  endDate: string | undefined;
  vcsProvider: VCSProviders[];
  status: FindingStatus[];
  project: string | undefined;
  repository: string | undefined;
  rule: string[];
  ruleTags: string[];
  rulePackVersions: string[];
};

const optionsRules = ref([] as string[]);
const optionsRuleTags = ref([] as string[]);
const startDate = ref(undefined) as Ref<string | undefined>;
const endDate = ref(undefined) as Ref<string | undefined>;

const selectedVcsProvider = ref([] as VCSProviders[]);
const selectedStatus = ref([] as FindingStatus[]);
const selectedProject = ref(undefined as string | undefined);
const selectedRepository = ref(undefined as string | undefined);
const selectedRule = ref([] as string[]);
const selectedRuleTags = ref([] as string[]);
const selectedRulePackVersions = ref([] as RulePackRead[]);

const emit = defineEmits(['on-filter-change']);

// const todaysDate = computed(() => {
//   const now = new Date();
//   const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
//   return new Date(today);
// });
// const minEndDate = computed(() => {
//   return startDate.value;
// });
// const endDateDisabled = computed(() => {
//   return startDate.value ? false : true;
// });

// function onStartDateChange() {
//   fetchAllDetectedRules();
//   handleFilterChange();
// }

// function onEndDateChange() {
//   fetchAllDetectedRules();
//   handleFilterChange();
// }

function onVcsProviderChange(vcsProvider: VCSProviders[]) {
  selectedVcsProvider.value = vcsProvider;
  fetchAllDetectedRules();
  handleFilterChange();
}

function onProjectChange(project: string | undefined) {
  selectedProject.value = project;
  fetchAllDetectedRules();
  handleFilterChange();
}

function onRepositoryChange(repository: string | undefined) {
  selectedRepository.value = repository;
  fetchAllDetectedRules();
  handleFilterChange();
}

function onFindingsStatusChange(status: FindingStatus[]) {
  selectedStatus.value = status;
  fetchAllDetectedRules();
  handleFilterChange();
}

function onRuleChange(rule: string[]) {
  selectedRule.value = rule;
  handleFilterChange();
}

function onRuleTagsChange(ruleTagsChange: string[]) {
  selectedRuleTags.value = ruleTagsChange;
  handleFilterChange();
}

function onRulePackVersionChange(rulePackVersionsChanged: RulePackRead[]) {
  selectedRulePackVersions.value = rulePackVersionsChanged;
  fetchAllDetectedRules();
  fetchRuleTags();
  handleFilterChange();
}

function setRulePackVersionsOnRulePackFilter(rulePackVersionsChanged: RulePackRead[]) {
  selectedRulePackVersions.value = rulePackVersionsChanged;
  fetchAllDetectedRules();
  fetchRuleTags();
}

function handleFilterChange() {
  // Refresh table data in Rule Analysis page
  const rulePackVersionsValues = [];
  if (selectedRulePackVersions.value) {
    for (const obj of selectedRulePackVersions.value) {
      rulePackVersionsValues.push(obj.version);
    }
  }
  const filterObj: RuleAnalysisFilter = {
    startDate: startDate.value,
    endDate: endDate.value,
    vcsProvider: selectedVcsProvider.value,
    status: selectedStatus.value,
    project: selectedProject.value,
    repository: selectedRepository.value,
    rule: selectedRule.value,
    rulePackVersions: rulePackVersionsValues,
    ruleTags: selectedRuleTags.value,
  };
  emit('on-filter-change', filterObj);
}

function fetchAllDetectedRules() {
  const rulePackVersionsFetched: string[] = [];
  if (selectedRulePackVersions.value.length === 0) {
    for (const obj of selectedRulePackVersions.value) {
      rulePackVersionsFetched.push(obj.version);
    }
  }
  RuleService.getAllDetectedRules(
    selectedStatus.value,
    selectedVcsProvider.value,
    selectedProject.value,
    selectedRepository.value,
    startDate.value,
    endDate.value,
    rulePackVersionsFetched,
  )
    .then((response) => {
      optionsRules.value = response.data;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function fetchRuleTags() {
  const rulePackVersionsFetched: string[] = [];
  if (selectedRulePackVersions.value) {
    for (const obj of selectedRulePackVersions.value) {
      rulePackVersionsFetched.push(obj.version);
    }
  }
  RulePackService.getRuleTagsByRulePackVersions(rulePackVersionsFetched)
    .then((response) => {
      optionsRuleTags.value = response.data;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
}

function applyRuleFilterInRuleAnalysisPage() {
  const store = useAuthUserStore();
  const selectedRules = [];
  const selectedVersions = [];
  const storePreviousRouteState = store.previousRouteState as PreviousRouteState;
  if (storePreviousRouteState) {
    selectedRules.push(storePreviousRouteState.ruleName);
    if (storePreviousRouteState.rulePackVersions) {
      for (const obj of storePreviousRouteState.rulePackVersions) {
        selectedVersions.push(obj.version);
      }
    }
    if (storePreviousRouteState.ruleTags) {
      selectedRuleTags.value = storePreviousRouteState.ruleTags;
    }
  }
  const sourceRoute = store.sourceRoute;
  const destinationRoute = store.destinationRoute;

  if (
    selectedRules.length > 0 &&
    sourceRoute === '/metrics/rule-metrics' &&
    destinationRoute === '/rule-analysis'
  ) {
    const filterObj: RuleAnalysisFilter = {
      startDate: startDate.value,
      endDate: endDate.value,
      vcsProvider: selectedVcsProvider.value,
      status: selectedStatus.value,
      project: selectedProject.value,
      repository: selectedRepository.value,
      rule: selectedRules,
      ruleTags: selectedRuleTags.value,
      rulePackVersions: selectedVersions,
    };

    //Populate rule analysis list based on rule filter
    emit('on-filter-change', filterObj);

    //Set rule fiter dropdown selected value
    selectedRule.value = selectedRules;
  } else {
    selectedRule.value = [];
  }
}

applyRuleFilterInRuleAnalysisPage();
</script>
