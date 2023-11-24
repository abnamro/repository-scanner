import Vue from 'vue';
import { PiniaVuePlugin, defineStore } from 'pinia';

Vue.use(PiniaVuePlugin);

export const useAuthUserStore = defineStore('authUser', {
  state: () => ({
    idToken: null,
    accessToken: null,
    sourceRoute: null,
    destinationRoute: null,
    firstName: null,
    lastName: null,
    email: null,
    previousRouteState: null,
  }),
  // If extra getters are needed.
  getters: {},
  actions: {
    update_auth_tokens(tokenData) {
      this.idToken = tokenData ? tokenData.id_token : null;
      this.accessToken = tokenData ? tokenData.access_token : null;
    },
    update_source_route(sourceRoute) {
      this.sourceRoute = sourceRoute ? sourceRoute : null;
    },
    update_destination_route(destinationRoute) {
      this.destinationRoute = destinationRoute ? destinationRoute : null;
    },
    update_user_details(userDetails) {
      this.firstName = userDetails ? userDetails.firstName : null;
      this.lastName = userDetails ? userDetails.lastName : null;
      this.email = userDetails ? userDetails.email : null;
    },
    update_previous_route_state(previousRouteState) {
      this.previousRouteState = previousRouteState ? previousRouteState : null;
    },
  },
  modules: {},
  persist: true,
});
