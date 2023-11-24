import { useAuthUserStore } from '@/store/index.js';
import Config from '@/configuration/config';
import AuthService from '@/services/auth-service';
import PushNotification from '@/utils/push-notification';

const axios = require('axios');

const AxiosConfig = {
  axiosSetUp() {
    axios.defaults.baseURL = `${Config.value('rescWebServiceUrl')}/v1`;

    axios.interceptors.request.use(
      function (config) {
        const store = useAuthUserStore();
        if (store.accessToken) {
          if (AuthService.isTokenExpired(store.accessToken)) {
            PushNotification.danger(
              'Your session has expired. You will be redirected to the Login page.',
              'Session Expired',
              3000
            );
            setTimeout(function () {
              AuthService.doLogOut();
            }, 5000);

            return {
              config,
              cancelToken: new axios.CancelToken((cancel) => cancel()),
            };
          } else {
            config.headers.Authorization = `Bearer ${store.accessToken}`;
            config.headers.Accept = 'application/json';
          }
        }
        return config;
      },
      function (error) {
        return Promise.reject(error);
      }
    );

    axios.interceptors.response.use(
      function (response) {
        if (response && response.status === 201) {
          PushNotification.success('Record saved successfully', 'Success', 5000);
        }
        return response;
      },
      function (error) {
        if (error.response && error.response.status && !isNaN(error.response.status)) {
          if (error.response.status === 403) {
            PushNotification.danger(
              'You do not have permission to access this resource. You will be redirected to the Login page.',
              'Access Denied',
              3000
            );
            setTimeout(function () {
              AuthService.doLogOut();
            }, 5000);
          } else {
            let error_msg = '';
            if (error.response.data.detail && error.response.status) {
              error_msg = `Status: ${error.response.status}, ${error.response.data.detail}`;
            } else {
              error_msg = error.message;
            }
            PushNotification.danger(error_msg, 'Error', 5000);
          }
        }

        return Promise.reject(error);
      }
    );
  },
  handleError(error) {
    if (error.response) {
      console.log(error.response.data);
      console.log(error.response.status);
      console.log(error.response.headers);
    } else if (error.request) {
      console.log(error.request);
    } else {
      console.log('Error', error.message);
    }
  },
};

export default AxiosConfig;
