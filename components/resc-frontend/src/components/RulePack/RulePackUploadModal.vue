<template>
  <div>
    <!-- Spinner -->
    <Spinner :active="spinnerActive" />
    <b-modal
      id="rule_pack_upload_modal"
      ref="rule_pack_upload_modal"
      size="lg"
      button-size="sm"
      :title="getModalTitle"
      @show="resetModal"
      @hidden="resetModal"
      @ok="handleOk"
    >
      <form ref="form" @submit.stop.prevent="submitForm">
        <div class="row">
          <div class="col-md-7">
            <b-form-group>
              <b-form-input
                id="version-input"
                placeholder="Enter Version"
                size="sm"
                v-model="version"
                :state="versionState"
                v-on:keyup="validateVersion"
                required
              ></b-form-input>
            </b-form-group>
          </div>
          <div class="col-md-5">
            <small><a href="https://semver.org/" target="_blank" rel="noopener">semver</a></small>
            <small> Example: 1.0.0</small>
          </div>
        </div>

        <div class="row">
          <div class="col-md-7">
            <b-form-group>
              <b-form-file
                v-model="file"
                placeholder="Choose a file or drop it here..."
                drop-placeholder="Drop file here..."
                accept=".toml"
                size="sm"
              ></b-form-file>
            </b-form-group>
          </div>
        </div>
      </form>

      <template #modal-footer>
        <div class="w-100">
          <b-button
            variant="prime"
            class="float-right"
            @click="handleOk"
            :disabled="(file && file.length == 0) || !versionState"
          >
            UPLOAD
          </b-button>
          <b-button variant="second" class="float-right mr-3" @click="hide"> CLOSE </b-button>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script>
import AxiosConfig from '@/configuration/axios-config.js';
import Spinner from '@/components/Common/Spinner.vue';
import PushNotification from '@/utils/push-notification';
import RulePackService from '@/services/rule-pack-service';
import spinnerMixin from '@/mixins/spinner.js';

export default {
  name: 'RulePackUploadModal',
  mixins: [spinnerMixin],
  data() {
    return {
      file: [],
      version: null,
      versionState: null,
    };
  },
  computed: {
    getModalTitle() {
      return `IMPORT RULEPACK`;
    },
  },
  methods: {
    show() {
      this.$refs.rule_pack_upload_modal.show();
    },
    hide() {
      this.version = null;
      this.file = [];
      this.versionState = null;
      this.$refs.rule_pack_upload_modal.hide();
    },
    resetModal() {
      this.version = null;
      this.file = [];
      this.versionState = null;
    },
    validateVersion() {
      let valid = false;
      this.versionState = false;
      const versionRegex = /^\d+(?:\.\d+){2}$/;
      if (versionRegex.test(this.version)) {
        valid = true;
        this.versionState = true;
      }
      return valid;
    },
    handleOk(bvModalEvt) {
      bvModalEvt.preventDefault();
      this.submitForm();
    },
    submitForm() {
      this.showSpinner();
      RulePackService.uploadRulePack(this.version, this.file)
        .then((response) => {
          this.$emit('on-file-upload-suceess');
          if (response && response.status === 200) {
            PushNotification.success('Rulepack uploaded successfully', 'Success', 5000);
          }
          this.hideSpinner();
          // Hide the modal manually
          this.$nextTick(() => {
            this.$refs['rule_pack_upload_modal'].hide();
          });
        })
        .catch((error) => {
          AxiosConfig.handleError(error);
          this.hideSpinner();
        });
    },
  },
  components: {
    Spinner,
  },
};
</script>
