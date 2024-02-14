<template>
  <div>
    <b-tab title="AUDIT" title-item-class="tab-pills">
      <SpinnerVue v-if="!loadedData" />
      <b-form
        class="pl-1 pr-4"
        @submit="onSubmit"
        @reset="onReset"
        v-if="show && loadedData"
        novalidate
      >
        <b-form-group
          label="Status"
          label-for="status-select"
          label-class="mr-sm-2 fw-bold small"
          invalid-feedback="Status is required"
          :state="statusState"
        >
          <b-form-select
            id="status-select"
            class="mb-2 mr-sm-2 mb-sm-0"
            size="sm"
            v-model="status"
            @change="checkFormValidity"
            required
          >
            <option v-for="status in statusList" :value="status.value" :key="status.id">
              {{ status.label }}
            </option>
          </b-form-select>
        </b-form-group>
        <b-form-group
          label="Comment"
          label-for="comment-textarea"
          label-class="mr-sm-2 fw-bold small"
          invalid-feedback="Maximum 255 characters are allowed"
          :state="commentState"
        >
          <b-form-textarea
            id="comment-textarea"
            placeholder="Enter Comment"
            size="sm"
            rows="3"
            trim
            v-model="comment"
            :state="commentState"
            v-on:keyup="checkFormValidity"
          ></b-form-textarea>
        </b-form-group>

        <b-button type="submit" variant="primary" :disabled="!isStatusValid || !isCommentValid">
          Save
        </b-button>
      </b-form>
    </b-tab>
  </div>
</template>

<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import CommonUtils, { type StatusOptionType } from '@/utils/common-utils';
import FindingsService from '@/services/findings-service';
import ScanFindingsService from '@/services/scan-findings-service';
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import type { DetailedFindingRead, FindingStatus } from '@/services/shema-to-types';
import { computed, nextTick, ref } from 'vue';

const loadedData = ref(false);

type Props = {
  finding: DetailedFindingRead;
};
const props = defineProps<Props>();

const finding = ref(props.finding);

const status = ref(props.finding.status ?? ('NOT_ANALYZED' as FindingStatus | ''));
const comment = ref(props.finding.comment ?? '');
const commentState = ref(true);
const statusState = ref(true);
const show = ref(true);
const statusList = ref([] as StatusOptionType[]);
const selectedFindingIds = ref([] as number[]);

const isStatusValid = computed(() => {
  return status.value !== '';
});
const isCommentValid = computed(() => {
  return comment.value !== '' && comment.value.length > 255 ? false : true;
});

function checkFormValidity() {
  let valid = false;
  if (isStatusValid.value && isCommentValid.value) {
    valid = true;
    statusState.value = true;
    commentState.value = true;
  } else if (!isStatusValid.value && isCommentValid.value) {
    statusState.value = false;
    commentState.value = true;
  } else if (isStatusValid.value && !isCommentValid.value) {
    statusState.value = true;
    commentState.value = false;
  } else {
    statusState.value = false;
    commentState.value = false;
  }
  return valid;
}

function onSubmit(event: Event) {
  event.preventDefault();
  if (!checkFormValidity()) {
    return;
  }

  loadedData.value = false;
  selectedFindingIds.value = [];
  if (finding.value.id_) {
    selectedFindingIds.value.push(finding.value.id_);
  }

  finding.value.status = status.value as FindingStatus;
  finding.value.comment = comment.value;

  FindingsService.auditFindings(
    selectedFindingIds.value,
    status.value as FindingStatus,
    comment.value,
  )
    .then(() => {
      loadedData.value = true;
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });
  reset();
}

function onReset(event: Event) {
  event.preventDefault();
}

function reset() {
  commentState.value = false;
  show.value = false;
  nextTick(() => {
    show.value = true;
  });
}

ScanFindingsService.getStatusList()
  .then((response) => {
    statusList.value = CommonUtils.parseStatusOptions(response.data as FindingStatus[]);
    loadedData.value = true;
  })
  .catch((error) => {
    AxiosConfig.handleError(error);
  });
</script>
