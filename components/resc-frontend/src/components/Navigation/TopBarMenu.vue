<template>
  <div class="topbar-menu-group" v-if="displayLoggedInUser">
    <b-button-toolbar aria-label="Toolbar with button groups and dropdown menu">
      <b-dropdown class="mx-1" right toggle-class="rounded-circle" no-caret>
        <template #button-content>
          <font-awesome-icon icon="user"></font-awesome-icon>
        </template>

        <b-dropdown-item disabled>
          <table>
            <tr>
              <td class="user-avatar-badge">
                <b-avatar
                  button
                  v-bind:text="avatarText"
                  class="align-baseline user-avatar"
                ></b-avatar>
              </td>
              <td>
                <span class="profile-menu-username">{{ userFullName }}</span
                ><br /><span class="profile-menu-email">{{ userEmail }}</span>
              </td>
            </tr>
          </table>
        </b-dropdown-item>

        <div>
          <b-dropdown-divider></b-dropdown-divider>
          <b-dropdown-item @click="logout">
            <font-awesome-icon class="sign-out-icon" icon="sign-out-alt"></font-awesome-icon>
            <span class="sign-out-text">Logout</span></b-dropdown-item
          >
        </div>
      </b-dropdown>
    </b-button-toolbar>
  </div>
</template>

<script>
import AuthService from '@/services/auth-service';
import Config from '@/configuration/config';

export default {
  name: 'TopBarMenu',
  data() {
    return {};
  },
  computed: {
    displayLoggedInUser() {
      const authenticationRequired = `${Config.value('authenticationRequired')}`;
      return authenticationRequired === 'true' ? true : false;
    },
    avatarText() {
      return this.$store.getters.firstName && this.$store.getters.lastName
        ? `${this.$store.getters.firstName.charAt(0)}${this.$store.getters.lastName.charAt(0)}`
        : null;
    },
    userFullName() {
      return this.$store.getters.firstName && this.$store.getters.lastName
        ? `${this.$store.getters.firstName} ${this.$store.getters.lastName}`
        : null;
    },
    userEmail() {
      return this.$store.getters.email ? `${this.$store.getters.email}` : null;
    },
  },
  methods: {
    logout() {
      AuthService.doLogOut();
    },
  },
};
</script>
<style scoped>
.topbar-menu-group {
  float: right;
  margin-top: 15px;
  margin-right: 10px;
}
</style>
