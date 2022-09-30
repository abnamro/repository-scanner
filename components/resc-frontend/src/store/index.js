import Vue from 'vue';
import Vuex from 'vuex';
import createPersistedState from 'vuex-persistedstate';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    idToken: null,
    accessToken: null,
    sourceRoute: null,
    destinationRoute: null,
    firstName: null,
    lastName: null,
    email: null,
    previousRouteState: null,
  },
  getters: {
    idToken: (state) => state.idToken,
    accessToken: (state) => state.accessToken,
    sourceRoute: (state) => state.sourceRoute,
    destinationRoute: (state) => state.destinationRoute,
    firstName: (state) => state.firstName,
    lastName: (state) => state.lastName,
    email: (state) => state.email,
    previousRouteState: (state) => state.previousRouteState,
  },
  mutations: {
    update_auth_tokens(state, tokenData) {
      state.idToken = tokenData ? tokenData.id_token : null;
      state.accessToken = tokenData ? tokenData.access_token : null;
    },
    update_source_route(state, sourceRoute) {
      state.sourceRoute = sourceRoute ? sourceRoute : null;
    },
    update_destination_route(state, destinationRoute) {
      state.destinationRoute = destinationRoute ? destinationRoute : null;
    },
    update_user_details(state, userDetails) {
      state.firstName = userDetails ? userDetails.firstName : null;
      state.lastName = userDetails ? userDetails.lastName : null;
      state.email = userDetails ? userDetails.email : null;
    },
    update_previous_route_state(state, previousRouteState) {
      state.previousRouteState = previousRouteState ? previousRouteState : null;
    },
  },
  actions: {},
  modules: {},
  plugins: [createPersistedState({ storage: window.localStorage })],
});
