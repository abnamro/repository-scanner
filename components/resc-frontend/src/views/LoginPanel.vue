<template>
  <div>
    <b-container class="login-container justify-content-md-center col-8">
      <b-row class="resc-header">
        <b-col>
          <!-- Application Name -->
          <div>Repository Scanner (RESC)</div>
        </b-col>
      </b-row>
      <b-row>
        <b-col>
          <!-- Auth warning -->
          <div class="warning-msg text-start fw-bold">
            Unauthorized access prohibited.<br />
            {{ ssoLoginPageMessage }}
          </div>
        </b-col>
      </b-row>
      <b-row>
        <b-col>
          <b-button variant="primary" class="mx-auto" v-on:click="login"> LOGIN </b-button>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script setup lang="ts">
import AuthService from '@/services/auth-service';
import AxiosConfig from '@/configuration/axios-config';
import Config from '@/configuration/config';
import { useAuthUserStore } from '@/store/index';
import { useRouter } from 'vue-router';

const ssoLoginPageMessage = `${Config.value('ssoLoginPageMessage')}`;
const router = useRouter();
const store = useAuthUserStore();

function login() {
  AuthService.requestLoginPage();
}

if (store.idToken && !AuthService.isTokenExpired(store.idToken)) {
  if (store.destinationRoute) {
    router.push(store.destinationRoute).catch((error) => {
      AxiosConfig.handleError(error);
    });
  } else {
    router.push('/').catch((error) => {
      AxiosConfig.handleError(error);
    });
  }
}
</script>

<style scoped>
.warning-msg {
  color: red;
}
.page-title {
  color: #939393;
}
.login-container {
  margin-top: 10%;
  border: 1px solid #6c757d;
  border-radius: 3px;
}
.login-container .row {
  padding-top: 15px;
  padding-bottom: 15px;
}
.resc-header {
  background: #01857a;
  color: white;
  font-weight: bold;
}
</style>
