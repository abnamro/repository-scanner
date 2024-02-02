import { mount } from '@vue/test-utils';
import { describe, expect, it, vi } from 'vitest';
import App from '@/views/LoginPanel.vue';
import AuthService from '@/services/auth-service';
import { createTestingPinia } from '@pinia/testing';

vi.mock('vue-router', async () => {
  const actual = await vi.importActual('vue-router');
  return {
    ...actual,
    useRoute: vi.fn(),
    useRouter: vi.fn(() => ({
      push: () => {},
    })),
  };
});

describe('LoginPanel tests', () => {
  const location = new URL('https://www.example.com');
  location.assign = vi.fn();
  location.replace = vi.fn();
  location.reload = vi.fn();

  delete window.location;
  window.location = location;

  it('Given a LoginPanel then LoginPanel will be displayed', () => {
    const wrapper = mount(App, {
      global: {
        stubs: ['router-view'],
        plugins: [
          createTestingPinia({
            initialState: {
              authUser: {
                idToken: null,
                accessToken: '12345',
                destinationRoute: 'resc',
                firstName: 'user',
                lastName: 'test',
                email: 'testuser@test.com',
              },
            },
          }),
        ],
      },
    });

    expect(wrapper.exists()).toBe(true);
  });

  it('Given a LoginPanel and an expired idToken then LoginPanel will be displayed', () => {
    const wrapper = mount(App, {
      global: {
        stubs: ['router-view', 'AuthService'],
        plugins: [
          createTestingPinia({
            initialState: {
              authUser: {
                idToken: '12345',
                accessToken: '12345',
                destinationRoute: 'resc',
                firstName: 'user',
                lastName: 'test',
                email: 'testuser@test.com',
              },
            },
          }),
        ],
      },
    });
    const spy = vi.spyOn(AuthService, 'requestLoginPage');

    expect(wrapper.exists()).toBe(true);
    wrapper.find('button').trigger('click');
    expect(spy).toHaveBeenCalledTimes(1);
  });
});
