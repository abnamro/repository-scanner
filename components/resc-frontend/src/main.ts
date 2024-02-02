import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { PiniaVuePlugin, createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import AxiosConfig from '@/configuration/axios-config';
import { importFA } from '@/assets/font-awesome';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, CategoryScale, PointElement);

import BootstrapVue from 'bootstrap-vue-next';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css';
import './styles/main.css';

const app = createApp(App);
app.use(PiniaVuePlugin);
app.use(router);
app.use(BootstrapVue);
importFA();
app.component('font-awesome-icon', FontAwesomeIcon);

AxiosConfig.axiosSetUp();

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.mount('#app');
