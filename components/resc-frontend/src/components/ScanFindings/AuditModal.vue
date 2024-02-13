<template>
  <div>
    <b-modal
      id="audit_modal"
      ref="audit_modal"
      size="lg"
      button-size="sm"
      :title="getModalTitle"
      @show="resetModal"
      @hidden="resetModal"
      @ok="handleOk"
    >
      <form ref="form" @submit.stop.prevent="handleSubmit">
        <b-form-group
          label="Status"
          label-for="audit-status"
          invalid-feedback="Status is required"
          :state="statusState"
        >
          <b-form-select
            id="audit-status"
            v-model="status"
            @change="checkFormValidity"
            :state="statusState"
            required
          >
            <option value="">-- Select Status</option>
            <option v-for="status in statusList" :value="status.value" :key="status.id">
              {{ status.label }}
            </option>
          </b-form-select>
        </b-form-group>

        <b-form-group
          label="Comment"
          label-for="comment-input"
          invalid-feedback="Maximum 255 characters are allowed"
          :state="commentState"
        >
          <b-form-textarea
            id="comment-input"
            placeholder="Enter Comment"
            rows="3"
            trim
            v-model="comment"
            :state="commentState"
            v-on:keyup="checkFormValidity"
          ></b-form-textarea>
        </b-form-group>
      </form>

      <template #modal-footer>
        <div class="w-100">
          <b-button
            variant="primary"
            class="float-right"
            v-on:click="handleOk"
            :disabled="!isStatusValid || !isCommentValid"
          >
            APPLY
          </b-button>
          <b-button variant="secondary" class="float-right mr-3" v-on:click="hide">
            CLOSE
          </b-button>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script setup lang="ts">
import AxiosConfig from '@/configuration/axios-config';
import CommonUtils, { type StatusOptionType } from '@/utils/common-utils';
import FindingsService from '@/services/findings-service';
import ScanFindingsService from '@/services/scan-findings-service';
import { computed, ref } from 'vue';
import type { FindingStatus } from '@/services/shema-to-types';
import type { BvTriggerableEvent } from 'bootstrap-vue-next';
import { nextTick } from 'vue';

const audit_modal = ref();

type Props = {
  selectedCheckBoxIds: number[];
};
const props = defineProps<Props>();

const emit = defineEmits(['update-audit']);

const comment = ref('');
const status = ref('NOT_ANALYZED' as FindingStatus | '');
const commentState = ref(true);
const statusState = ref(true);
const statusList = ref([] as StatusOptionType[]);

const getModalTitle = computed(() => {
  return `AUDIT ${props.selectedCheckBoxIds.length} FINDINGS`;
});
const isStatusValid = computed(() => {
  return status.value !== '';
});
const isCommentValid = computed(() => {
  return comment.value.length > 255 ? false : true;
});

function show() {
  audit_modal.value.show();
}

function hide() {
  audit_modal.value.hide();
}

// ! TODO is this really necessary?
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

function resetModal() {
  status.value = 'NOT_ANALYZED';
  comment.value = '';
  statusState.value = true;
  commentState.value = true;
}

function handleOk(bvModalEvt: BvTriggerableEvent | MouseEvent) {
  bvModalEvt.preventDefault();
  handleSubmit();
}

function handleSubmit() {
  // Don't close the modal if form is invalid
  if (!checkFormValidity()) {
    return;
  }

  FindingsService.auditFindings(
    props.selectedCheckBoxIds,
    status.value as FindingStatus,
    comment.value,
  )
    .then(() => {
      emit('update-audit', status, comment);
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
    });

  // Hide the modal manually
  nextTick(() => {
    audit_modal.value.hide();
  });
}

ScanFindingsService.getStatusList()
  .then((response) => {
    statusList.value = CommonUtils.parseStatusOptions(response.data as FindingStatus[]);
  })
  .catch((error) => {
    AxiosConfig.handleError(error);
  });

defineExpose({ show });
</script>
