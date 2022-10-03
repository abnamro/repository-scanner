import Vue from 'vue';
import BVToastPlugin from 'bootstrap-vue';

import PushNotification from '@/utils/push-notification';

describe('Testing PushNotification', () => {
  Vue.use(BVToastPlugin);

  it('primary notification', async () => {
    const spy = jest.spyOn(PushNotification, 'notify');
    PushNotification.primary('primary message', 'primary title', 1000);
    expect(spy).toHaveBeenCalledWith('primary message', 'primary title', 'primary', 1000);
  });

  it('secondary notification', async () => {
    const spy = jest.spyOn(PushNotification, 'notify');
    PushNotification.secondary('secondary message', 'secondary title', 1000);
    expect(spy).toHaveBeenCalledWith('secondary message', 'secondary title', 'secondary', 1000);
  });

  it('danger notification', async () => {
    const spy = jest.spyOn(PushNotification, 'danger');
    PushNotification.danger('danger message', 'danger title', 1000);
    expect(spy).toHaveBeenCalledWith('danger message', 'danger title', 1000);
  });

  it('warning notification', async () => {
    const spy = jest.spyOn(PushNotification, 'warning');
    PushNotification.warning('warning message', 'warning title', 1000);
    expect(spy).toHaveBeenCalledWith('warning message', 'warning title', 1000);
  });

  it('success notification', async () => {
    const spy = jest.spyOn(PushNotification, 'success');
    PushNotification.success('success message', 'success title', 1000);
    expect(spy).toHaveBeenCalledWith('success message', 'success title', 1000);
  });

  it('info notification', async () => {
    const spy = jest.spyOn(PushNotification, 'info');
    PushNotification.info('info message', 'info title', 1000);
    expect(spy).toHaveBeenCalledWith('info message', 'info title', 1000);
  });
});
