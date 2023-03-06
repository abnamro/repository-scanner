<template>
  <div>
    <b-tab title="INFO" active title-item-class="tab-pills">
      <div class="row">
        <!-- Finding info -->
        <div class="col-md-6">
          <b-card-text
            ><span class="font-weight-bold">Commit ID: </span
            ><a class="custom-link" v-bind:href="finding.commit_url" target="_blank">{{
              finding.commit_id
            }}</a></b-card-text
          >
          <b-card-text
            ><span class="font-weight-bold">File Path: </span>{{ finding.file_path }}</b-card-text
          >
          <b-card-text
            ><span class="font-weight-bold">Line Number: </span
            >{{ finding.line_number }}</b-card-text
          >
          <b-card-text
            ><span class="font-weight-bold">Position: </span
            >{{ finding.column_start }} - {{ finding.column_end }}</b-card-text
          >
          <b-card-text
            ><span class="font-weight-bold">Author: </span>{{ finding.author }}</b-card-text
          >
          <b-card-text
            ><span class="font-weight-bold">Email: </span>{{ finding.email }}</b-card-text
          >
          <b-card-text
            ><span class="font-weight-bold">Commit Time: </span
            >{{ finding.commit_timestamp }}</b-card-text
          >
          <b-card-text
            ><span class="font-weight-bold">Commit Message: </span
            >{{ finding.commit_message | truncate(50, '...') }}</b-card-text
          >
          <b-card-text
            ><span class="font-weight-bold">Rulepack: </span>{{ finding.rule_pack }}</b-card-text
          >
        </div>

        <!-- Audit -->
        <div class="col-md-6">
          <div class="ml-4">
            <b-form @submit="onSubmit" @reset="onReset" v-if="show" novalidate>
              <b-form-group
                label="Status"
                label-for="status-select"
                label-class="mr-sm-2 font-weight-bold small"
              >
                <b-form-select
                  id="status-select"
                  class="mb-2 mr-sm-2 mb-sm-0"
                  size="sm"
                  v-model="form.status"
                  @change="checkFormValidity"
                >
                  <option v-for="status in statusList" :value="status.value" :key="status.id">
                    {{ status.label }}
                  </option>
                </b-form-select>
              </b-form-group>
              <b-form-group
                label="Comment"
                label-for="comment-textarea"
                label-class="mr-sm-2 font-weight-bold small"
                invalid-feedback="Maximum 255 characters are allowed"
                :state="commentState"
              >
                <b-form-textarea
                  id="comment-textarea"
                  v-model="form.comment"
                  placeholder="Enter Comment"
                  size="sm"
                  rows="3"
                  trim
                  :state="commentState"
                  v-on:keyup="checkFormValidity"
                ></b-form-textarea>
              </b-form-group>

              <b-button type="submit" variant="prime" :disabled="!isCommentValid">Save</b-button>
            </b-form>
          </div>
        </div>
      </div>
    </b-tab>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import FindingsService from '@/services/findings-service';
import PushNotification from '@/utils/push-notification';
import ScanFindingsService from '@/services/scan-findings-service';

export default {
  name: 'FindingTab',
  data() {
    return {
      selectedFindingIds: [],
      statusList: [],
      commentState: null,
      form: {
        status: this.finding.status,
        comment: this.finding.comment ? this.finding.comment : '',
      },
      show: true,
    };
  },
  props: {
    finding: {
      type: Object,
      required: true,
    },
    repository: {
      type: Object,
      required: true,
    },
  },
  filters: {
    truncate: function (text, length, suffix) {
      if (text.length > length) {
        return text.substring(0, length) + suffix;
      } else {
        return text;
      }
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
    onSubmit(event) {
      event.preventDefault();
      this.selectedFindingIds = [];
      if (this.finding.id_) {
        this.selectedFindingIds.push(this.finding.id_);
      }
      this.finding.status = this.form.status;
      this.finding.comment = this.form.comment;

      FindingsService.auditFindings(
        this.selectedFindingIds,
        this.finding.status,
        this.finding.comment
      )
        .then(() => {
          PushNotification.success('Audit saved successfully', 'Success', 5000);
        })
        .catch((error) => {
          PushNotification.danger(error.message, 'Error', 5000);
        });
      this.reset();
    },

    onReset(event) {
      event.preventDefault();
    },

    reset() {
      this.commentState = null;
      this.show = false;
      this.$nextTick(() => {
        this.show = true;
      });
    },

    checkFormValidity() {
      this.commentState = this.isCommentValid ? true : false;
      return this.commentState;
    },
  },
  computed: {
    isCommentValid() {
      return this.form.comment && this.form.comment.length > 255 ? false : true;
    },
  },
  created() {
    this.fetchStatuses();
  },
};
</script>
<style scoped>
.custom-link {
  color: #005e5d;
}
a:hover {
  color: #005e5d;
}
</style>
