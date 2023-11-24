import Vue from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import AxiosConfig from '@/configuration/axios-config';

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  CategoryScale,
  PointElement,
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, CategoryScale, PointElement);

import BootstrapVue from 'bootstrap-vue';
import { library } from '@fortawesome/fontawesome-svg-core';
import {
  faChartLine,
  faCodeBranch,
  faHammer,
  faChartBar,
  faAngleDoubleLeft,
  faAngleRight,
  faUser,
  faSignOutAlt,
  faCog,
  faShieldAlt,
  faDownload,
  faCheckCircle,
  faTimesCircle,
  faArrowUp,
  faArrowDown,
  faTrophy,
  faInfoCircle,
  faThumbsDown,
  faMedal,
  faAward,
} from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import './styles/main.css';

library.add(
  faChartLine,
  faCodeBranch,
  faHammer,
  faChartBar,
  faAngleDoubleLeft,
  faAngleRight,
  faUser,
  faSignOutAlt,
  faCog,
  faShieldAlt,
  faDownload,
  faCheckCircle,
  faTimesCircle,
  faArrowUp,
  faArrowDown,
  faTrophy,
  faInfoCircle,
  faThumbsDown,
  faMedal,
  faAward
);

Vue.config.productionTip = false;

Vue.use(BootstrapVue);
Vue.component('font-awesome-icon', FontAwesomeIcon);

AxiosConfig.axiosSetUp();

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

new Vue({
  router,
  pinia,
  render: (h) => h(App),
}).$mount('#app');
