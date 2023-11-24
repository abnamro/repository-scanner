import { useAuthUserStore } from '@/store/index';
import { setActivePinia, createPinia } from 'pinia';

describe('Store management unit test', () => {
  afterEach(() => {
    jest.resetModules();
    jest.clearAllMocks();
  });

  describe('store Mutations', () => {
    beforeEach(() => {
      // creates a fresh pinia and makes it active
      // so it's automatically picked up by any useStore() call
      // without having to pass it to it: `useStore(pinia)`
      setActivePinia(createPinia());
    });

    it('Check update_auth_tokens', async () => {
      const store = useAuthUserStore();
      await store.update_auth_tokens(null);
      await expect(store.accessToken).toBe(null);
      await expect(store.idToken).toBe(null);
    });

    it('Check update_destination_route', async () => {
      const store = useAuthUserStore();
      await store.update_destination_route(null);
      await expect(store.destinationRoute).toBe(null);
    });

    it('Check update_user_details', async () => {
      const store = useAuthUserStore();
      await store.update_user_details(null);
      await expect(store.firstName).toBe(null);
      await expect(store.lastName).toBe(null);
      await expect(store.email).toBe(null);
    });
  });
});
