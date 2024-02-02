<template>
  <div></div>
</template>
<script setup lang="ts">
import AuthService from '@/services/auth-service';
import { onMounted } from 'vue';

onMounted(() => {
  const promise = AuthService.doLogin();
  if (!promise) {
    AuthService.doLogOut();
  }
});
</script>
