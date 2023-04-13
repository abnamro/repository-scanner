<template>
  <div>
    <b-tab title="AUDIT" title-item-class="tab-pills">
      <!-- Spinner -->
      <Spinner :active="spinnerActive" />

      <b-form class="pl-1 pr-4" @submit="onSubmit" @reset="onReset" v-if="show" novalidate>
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
    </b-tab>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import FindingsService from '@/services/findings-service';
import ScanFindingsService from '@/services/scan-findings-service';
import Spinner from '@/components/Common/Spinner.vue';
import spinnerMixin from '@/mixins/spinner.js';

export default {
  name: 'AuditTab',
  mixins: [spinnerMixin],
  props: {
    finding: {
      type: Object,
      required: true,
    },
  },
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
      this.showSpinner();
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
          this.hideSpinner();
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
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
  components: {
    Spinner,
  },
};
</script>
