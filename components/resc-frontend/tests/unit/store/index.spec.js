import store from '@/store/index';

describe('Store management unit test', () => {
  afterEach(() => {
    jest.resetModules();
    jest.clearAllMocks();
  });

  describe('store Mutations', () => {
    it('Check update_auth_tokens', async () => {
      await store.commit('update_auth_tokens', null);
      await expect(store.state.accessToken).toBe(null);
      await expect(store.state.idToken).toBe(null);
      await expect(store.getters.idToken).toBe(null);
      await expect(store.getters.accessToken).toBe(null);
    });

    it('Check update_destination_route', async () => {
      await store.commit('update_destination_route', null);
      await expect(store.state.destinationRoute).toBe(null);
      await expect(store.getters.destinationRoute).toBe(null);
    });

    it('Check update_user_details', async () => {
      await store.commit('update_user_details', null);
      await expect(store.state.firstName).toBe(null);
      await expect(store.state.lastName).toBe(null);
      await expect(store.state.email).toBe(null);
      await expect(store.getters.firstName).toBe(null);
      await expect(store.getters.lastName).toBe(null);
      await expect(store.getters.email).toBe(null);
    });
  });
});
