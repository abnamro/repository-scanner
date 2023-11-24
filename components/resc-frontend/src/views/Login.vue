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
          <div class="warning-msg text-left font-weight-bold">
            Unauthorized access prohibited.<br />
            {{ ssoLoginPageMessage }}
          </div>
        </b-col>
      </b-row>
      <b-row>
        <b-col>
          <b-button variant="prime" class="mx-auto" @click="login"> LOGIN </b-button>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import AuthService from '@/services/auth-service';
import AxiosConfig from '@/configuration/axios-config.js';
import Config from '@/configuration/config';

export default {
  name: 'Login',
  data() {
    return {
      ssoLoginPageMessage: `${Config.value('ssoLoginPageMessage')}`,
    };
  },
  methods: {
    login() {
      AuthService.requestLoginPage();
    },
  },
  created() {
    if (this.$store.idToken && !AuthService.isTokenExpired(this.$store.idToken)) {
      if (this.$store.destinationRoute) {
        this.$router.push(this.$store.destinationRoute).catch((error) => {
          AxiosConfig.handleError(error);
        });
      } else {
        this.$router.push('/').catch((error) => {
          AxiosConfig.handleError(error);
        });
      }
    }
  },
};
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
