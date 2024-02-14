import { useAuthUserStore } from '@/store/index';
import Config from '@/configuration/config';
import AuthService from '@/services/auth-service';
import PushNotification from '@/utils/push-notification';
import axios, {
  type AxiosRequestConfig,
  type AxiosRequestHeaders,
  type AxiosResponse,
  type Canceler,
} from 'axios';
import type { Swr } from '@/services/shema-to-types';

const AxiosConfig = {
  axiosSetUp() {
    axios.defaults.baseURL = `${Config.value('rescWebServiceUrl')}/v1`;

    axios.interceptors.request.use(
      // @ts-expect-error
      function (config: AxiosRequestConfig) {
        const store = useAuthUserStore();
        if (store.accessToken) {
          if (AuthService.isTokenExpired(store.accessToken)) {
            PushNotification.danger(
              'Your session has expired. You will be redirected to the Login page.',
              'Session Expired',
              3000,
            );
            setTimeout(function () {
              AuthService.doLogOut();
            }, 5000);

            return {
              config,
              cancelToken: new axios.CancelToken((cancel: Canceler) => cancel()),
            };
          } else {
            // ts is complaining that config.header might be null
            // todo: add check later ?
            (config.headers as AxiosRequestHeaders).Authorization = `Bearer ${store.accessToken}`;
            (config.headers as AxiosRequestHeaders).Accept = 'application/json';
          }
        }
        return config;
      },
      function (error: Swr) {
        return Promise.reject(error);
      },
    );

    axios.interceptors.response.use(
      function (response: AxiosResponse): AxiosResponse {
        if (response && response.status === 201) {
          PushNotification.success('Record saved successfully', 'Success', 5000);
        }
        return response;
      },
      function (error: Swr): Promise<never> {
        if (error.response && error.response.status && !isNaN(error.response.status)) {
          if (error.response.status === 403) {
            PushNotification.danger(
              'You do not have permission to access this resource. You will be redirected to the Login page.',
              'Access Denied',
              3000,
            );
            setTimeout(function () {
              AuthService.doLogOut();
            }, 5000);
          } else {
            let errorMsg = '';
            if (error.response.data.detail && error.response.status) {
              errorMsg = `Status: ${error.response.status}, ${error.response.data.detail}`;
            } else {
              errorMsg = error.message;
            }
            PushNotification.danger(errorMsg, 'Error', 5000);
          }
        }

        return Promise.reject(error);
      },
    );
  },
  handleError(error: Swr) {
    if (error.response) {
      console.log(error.response.data);
      console.log(error.response.status);
      console.log(error.response.headers);
    } else if (error.request) {
      console.log(error.request);
    } else {
      console.log('Error', error.message);
      console.log(error);
    }
  },
};

export default AxiosConfig;
