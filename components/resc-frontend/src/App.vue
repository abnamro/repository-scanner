<template>
  <div id="app">
    <sidebar-menu
      :menu="sidebarNavigationMenu"
      :collapsed="sidebarCollapsed"
      @toggle-collapse="onToggleCollapse"
      :show-one-child="true"
      :disable-hover="true"
      width="250px"
      v-if="showMenu"
    >
      <font-awesome-icon
        slot="toggle-icon"
        icon="angle-double-left"
        :rotation="sidebarCollapsed ? 180 : null"
      />
      <font-awesome-icon slot="dropdown-icon" icon="angle-right" />
    </sidebar-menu>
    <TopBarMenu v-if="showMenu" />
    <div
      id="content-wrapper"
      :class="{
        'sidebar-closed': sidebarCollapsed,
        'sidebar-opened': !sidebarCollapsed,
      }"
    >
      <div class="container-fluid">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import { SidebarMenu } from 'vue-sidebar-menu';
import TopBarMenu from '@/components/Navigation/TopBarMenu.vue';
import Navigation from '@/components/Navigation/Navigation';
import 'vue-sidebar-menu/dist/vue-sidebar-menu.css';

export default {
  name: 'App',
  components: {
    SidebarMenu,
    TopBarMenu,
  },
  data() {
    return {
      sidebarCollapsed: false,
      sidebarNavigationMenu: Navigation.sidebarMenu,
    };
  },
  methods: {
    onToggleCollapse(collapsed) {
      this.sidebarCollapsed = collapsed;
    },
  },
  computed: {
    showMenu() {
      if (this.$route.name === 'Login') {
        this.onToggleCollapse(true);
        return false;
      }
      return true;
    },
  },
};
</script>
