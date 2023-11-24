import { shallowMount, createLocalVue } from '@vue/test-utils';
import App from '@/App';
import VueRouter from 'vue-router';
import TopBarMenu from '@/components/Navigation/TopBarMenu.vue';
import Navigation from '@/components/Navigation/Navigation';
import { defineStore, PiniaVuePlugin } from 'pinia';
import Vue from 'vue';
import { SidebarMenu } from 'vue-sidebar-menu';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

describe('App.vue unit tests', () => {
  let wrapper;
  const localVue = createLocalVue();
  localVue.use(VueRouter);
  const router = new VueRouter();
  Vue.use(PiniaVuePlugin);

  let store = defineStore('authUser', {
    state: () => ({
      idToken: '12345',
      accessToken: '12345',
      destinationRoute: 'resc',
      firstName: 'testuser',
      lastName: 'test',
      email: 'testuser@test.com',
    }),
    getters: {},
    actions: {},
  });

  function initMountApp() {
    wrapper = shallowMount(App, {
      router,
      localVue,
      store,
      components: {
        SidebarMenu: SidebarMenu,
        TopBarMenu: TopBarMenu,
        fontAwesomeIcon: FontAwesomeIcon,
      },
      data() {
        return {
          sidebarCollapsed: false,
          sidebarNavigationMenu: Navigation.sidebarMenu,
        };
      },
    });
  }

  beforeEach(() => {
    initMountApp();
  });

  it('Given an App When login then Top bar and SideMenubar will be displayed', () => {
    expect(wrapper.exists()).toBe(true);
    expect(wrapper.findComponent(TopBarMenu).exists()).toBe(true);
    expect(wrapper.findComponent(SidebarMenu).exists()).toBe(true);
  });
});
