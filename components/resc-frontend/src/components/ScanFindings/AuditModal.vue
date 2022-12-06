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
            variant="prime"
            class="float-right"
            @click="handleOk"
            :disabled="!isStatusValid || !isCommentValid"
          >
            APPLY
          </b-button>
          <b-button variant="second" class="float-right mr-3" @click="hide"> CLOSE </b-button>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import FindingsService from '@/services/findings-service';
import PushNotification from '@/utils/push-notification';
import ScanFindingsService from '@/services/scan-findings-service';

export default {
  name: 'AuditModal',
  props: {
    selectedCheckBoxIds: {
      type: Array,
      required: true,
    },
  },
  emits: ['update-audit'],
  data() {
    return {
      comment: '',
      status: '',
      commentState: null,
      statusState: null,
      statusList: [],
    };
  },
  computed: {
    getModalTitle() {
      return `AUDIT FINDINGS (${this.selectedCheckBoxIds.length})`;
    },
    isStatusValid() {
      return this.status && this.status !== null;
    },
    isCommentValid() {
      return this.comment && this.comment.length > 255 ? false : true;
    },
  },
  methods: {
    fetchStatuses() {
      ScanFindingsService.getStatusList()
        .then((response) => {
          this.statusList = ScanFindingsService.parseStatusOptions(response.data);
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
        });
    },
    show() {
      this.$refs.audit_modal.show();
    },
    hide() {
      this.$refs.audit_modal.hide();
    },
    checkFormValidity() {
      let valid = false;
      if (this.isStatusValid && this.isCommentValid) {
        valid = true;
        this.statusState = true;
        this.commentState = true;
      } else if (!this.isStatusValid && this.isCommentValid) {
        this.statusState = false;
        this.commentState = true;
      } else if (this.isStatusValid && !this.isCommentValid) {
        this.statusState = true;
        this.commentState = false;
      } else {
        this.statusState = false;
        this.commentState = false;
      }
      return valid;
    },
    resetModal() {
      this.status = '';
      this.comment = '';
      this.statusState = null;
      this.commentState = null;
    },
    handleOk(bvModalEvt) {
      bvModalEvt.preventDefault();
      this.handleSubmit();
    },
    handleSubmit() {
      // Don't close the modal if form is invalid
      if (!this.checkFormValidity()) {
        return;
      }

      FindingsService.auditFindings(this.selectedCheckBoxIds, this.status, this.comment)
        .then(() => {
          this.$emit('update-audit', this.status, this.comment);
          PushNotification.success('Audit saved successfully', 'Success', 5000);
        })
        .catch((error) => {
          PushNotification.danger(error.message, 'Error', 5000);
        });

      // Hide the modal manually
      this.$nextTick(() => {
        this.$refs['audit_modal'].hide();
      });
    },
  },
  created() {
    this.fetchStatuses();
  },
};
</script>
