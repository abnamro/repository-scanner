import { useToast } from 'bootstrap-vue-next';
import type { BaseColorVariant } from 'node_modules/bootstrap-vue-next/dist/src/types';

const c = useToast();

const PushNotification = {
  notify(
    message: string,
    titlePush: string,
    variantType: keyof BaseColorVariant,
    autoHideDelay: number,
  ) {
    c?.show({
      title: titlePush,
      body: message,
      pos: 'top-right',
      variant: variantType,
      value: autoHideDelay,
      interval: 100,
      autoHide: true,
      solid: true,
    });
  },
  primary(message: string, title: string, autoHideDelay: number) {
    PushNotification.notify(message, title, 'primary', autoHideDelay);
  },
  secondary(message: string, title: string, autoHideDelay: number) {
    PushNotification.notify(message, title, 'secondary', autoHideDelay);
  },
  danger(message: string, title: string, autoHideDelay: number) {
    PushNotification.notify(message, title, 'danger', autoHideDelay);
  },
  warning(message: string, title: string, autoHideDelay: number) {
    PushNotification.notify(message, title, 'warning', autoHideDelay);
  },
  success(message: string, title: string, autoHideDelay: number) {
    PushNotification.notify(message, title, 'success', autoHideDelay);
  },
  info(message: string, title: string, autoHideDelay: number) {
    PushNotification.notify(message, title, 'info', autoHideDelay);
  },
};

export default PushNotification;
