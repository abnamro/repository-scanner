<template>
  <div>
    <SpinnerVue v-if="!loadedData" />
    <b-modal
      id="rule_pack_upload_modal"
      ref="rule_pack_upload_modal"
      size="lg"
      button-size="sm"
      title="IMPORT RULEPACK"
      @show="resetModal"
      @hidden="resetModal"
      @ok="handleOk"
      :static="true"
    >
      <form ref="form" @submit.stop.prevent="submitForm">
        <div class="row">
          <div class="col-md-7">
            <b-form-group>
              <b-form-input
                id="versionInput"
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
                if="fileDrop"
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
            variant="primary"
            class="float-right"
            v-on:click="handleOk"
            :disabled="(file && file.length == 0) || !versionState"
          >
            UPLOAD
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
import SpinnerVue from '@/components/Common/SpinnerVue.vue';
import PushNotification from '@/utils/push-notification';
import RulePackService from '@/services/rule-pack-service';
import { nextTick, ref, type Ref } from 'vue';
import type { BvEvent } from 'bootstrap-vue-next';

const loadedData = ref(true);
const rule_pack_upload_modal = ref();

const file = ref([] as File[]);
const version = ref('');
const versionState = ref(null) as Ref<boolean | null>;
const emit = defineEmits(['on-file-upload-suceess']);

function show(): void {
  rule_pack_upload_modal.value.show();
}

function hide(): void {
  version.value = '';
  file.value = [];
  versionState.value = null;
  rule_pack_upload_modal.value.hide();
}

function resetModal(): void {
  version.value = '';
  file.value = [];
  versionState.value = null;
}

function validateVersion(): boolean {
  versionState.value = false;
  const versionRegex = /^\d+(?:\.\d+){2}$/;
  if (versionRegex.test(version.value)) {
    versionState.value = true;
    return true;
  }
  return false;
}

function handleOk(bvModalEvt: BvEvent | MouseEvent) {
  bvModalEvt.preventDefault();
  submitForm();
}

function submitForm() {
  loadedData.value = false;
  RulePackService.uploadRulePack(version.value, file.value[0])
    .then((response) => {
      emit('on-file-upload-suceess');
      if (response && response.status === 200) {
        PushNotification.success('Rulepack uploaded successfully', 'Success', 5000);
      }
      loadedData.value = true;
      // Hide the modal manually
      nextTick(() => {
        rule_pack_upload_modal.value.hide();
      });
    })
    .catch((error) => {
      AxiosConfig.handleError(error);
      loadedData.value = false;
    });
}

defineExpose({ show });
</script>
