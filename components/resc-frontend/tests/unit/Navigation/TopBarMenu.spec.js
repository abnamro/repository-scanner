import { shallowMount, createLocalVue } from '@vue/test-utils';
import App from '@/components/Navigation/TopBarMenu';
import VueRouter from 'vue-router';
import Vuex from 'vuex';
import Vue from 'vue';
import { BAvatar, BButtonToolbar, BDropdown, BDropdownDivider, BDropdownItem } from 'bootstrap-vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

describe('TopBarMenu.vue unit tests', () => {
  let wrapper;
  const localVue = createLocalVue();
  localVue.use(VueRouter);
  const router = new VueRouter();
  Vue.use(Vuex);

  let store = new Vuex.Store({
    state: {
      idToken: '12345',
      accessToken: '12345',
      destinationRoute: 'resc',
      firstName: 'testuser',
      lastName: 'test',
      email: 'testuser@test.com',
    },
    getters: {
      idToken: (state) => state.idToken,
      accessToken: (state) => state.accessToken,
      destinationRoute: (state) => state.destinationRoute,
      firstName: (state) => state.firstName,
      lastName: (state) => state.lastName,
      email: (state) => state.email,
    },
    mutations: {},
    actions: {},
  });

  function initMountApp() {
    wrapper = shallowMount(App, {
      router,
      localVue,
      store,
      components: {
        BButtonToolbar: BButtonToolbar,
        BDropdown: BDropdown,
        FontAwesomeIcon: FontAwesomeIcon,
        BDropdownItem: BDropdownItem,
        BAvatar: BAvatar,
        BDropdownDivider: BDropdownDivider,
      },
    });
  }

  beforeEach(() => {
    initMountApp();
  });

  it('Given TopBarMenu template structure check', () => {
    expect(wrapper.exists()).toBe(true);
  });
});
