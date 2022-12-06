import { BToast } from 'bootstrap-vue';

const PushNotification = {
  notify(message, title, variant, autoHideDelay) {
    new BToast().$bvToast.toast(message, {
      title: title,
      variant: variant,
      autoHideDelay: autoHideDelay,
      solid: true,
    });
  },
  primary(message, title, autoHideDelay) {
    PushNotification.notify(message, title, 'primary', autoHideDelay);
  },
  secondary(message, title, autoHideDelay) {
    PushNotification.notify(message, title, 'secondary', autoHideDelay);
  },
  danger(message, title, autoHideDelay) {
    PushNotification.notify(message, title, 'danger', autoHideDelay);
  },
  warning(message, title, autoHideDelay) {
    PushNotification.notify(message, title, 'warning', autoHideDelay);
  },
  success(message, title, autoHideDelay) {
    PushNotification.notify(message, title, 'success', autoHideDelay);
  },
  info(message, title, autoHideDelay) {
    PushNotification.notify(message, title, 'info', autoHideDelay);
  },
};

export default PushNotification;
