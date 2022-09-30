<template>
  <div></div>
</template>

<script>
import AuthService from '@/services/auth-service';

export default {
  name: 'LoginCallback',
  mounted() {
    const promise = AuthService.doLogin();
    if (!promise) {
      AuthService.doLogOut();
    }
  },
};
</script>
