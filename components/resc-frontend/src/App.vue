<template>
  <SidebarMenu
    :menu="sidebarNavigationMenu"
    v-model:collapsed="sidebarCollapsed"
    :show-one-child="true"
    :disable-hover="true"
    width="250px"
    @update:collapsed="onToggleCollapse"
    v-if="showMenu"
  />
  <TopBarMenu v-if="showMenu" />
  <div
    id="content-wrapper"
    :class="{
      'sidebar-closed': sidebarCollapsed,
      'sidebar-opened': !sidebarCollapsed,
    }"
  >
    <div class="container-fluid">
      <RouterView />
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, RouterView } from 'vue-router';
import { SidebarMenu } from 'vue-sidebar-menu';
import TopBarMenu from '@/components/Navigation/TopBarMenu.vue';
import { sidebarMenu } from '@/components/Navigation/Navigation';
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css';

const route = useRoute();

const sidebarNavigationMenu = sidebarMenu;
const sidebarCollapsed = ref(false);

function onToggleCollapse(collapsed: boolean) {
  sidebarCollapsed.value = collapsed;
}

const showMenu = computed(() => {
  if (route?.name === 'Login') {
    onToggleCollapse(true);
    return false;
  }
  return true;
});
</script>
