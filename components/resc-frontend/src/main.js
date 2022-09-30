import Vue from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
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
  faTimesCircle
);

Vue.config.productionTip = false;

Vue.use(BootstrapVue);
Vue.component('font-awesome-icon', FontAwesomeIcon);

AxiosConfig.axiosSetUp();

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount('#app');
