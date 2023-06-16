import Vue from 'vue';
import VueRouter from 'vue-router';
import Config from '@/configuration/config';
import FindingMetrics from '@/components/Metrics/FindingMetrics';
import AuditMetrics from '@/components/Metrics/AuditMetrics';
import Store from '@/store/index.js';
import Analytics from '@/views/Analytics';
import Repositories from '@/views/Repositories';
import ScanFindings from '@/views/ScanFindings';
import RuleAnalysis from '@/views/RuleAnalysis';
import RulePacks from '@/views/RulePacks';
import RuleMetrics from '@/components/Metrics/RuleMetrics';
import Login from '@/views/Login';
import LoginCallback from '@/components/Login/LoginCallback';
import AuthService from '@/services/auth-service';

Vue.use(VueRouter);

const authenticationRequired = `${Config.value('authenticationRequired')}`;

const routes = [
  {
    path: '/',
    name: 'Analytics',
    component: Analytics,
  },
  {
    path: '/repositories',
    name: 'Repositories',
    component: Repositories,
  },
  {
    path: '/findings/:scanId',
    name: 'ScanFindings',
    component: ScanFindings,
    props: true,
  },
  {
    path: '/rule-analysis',
    name: 'RuleAnalysis',
    component: RuleAnalysis,
  },
  {
    path: '/metrics/rule-metrics',
    name: 'RuleMetrics',
    component: RuleMetrics,
  },
  {
    path: '/metrics/finding-metrics',
    name: 'FindingMetrics',
    component: FindingMetrics,
  },
  {
    path: '/metrics/audit-metrics',
    name: 'AuditMetrics',
    component: AuditMetrics,
  },
  {
    path: '/rulepacks',
    name: 'RulePacks',
    component: RulePacks,
  },
  {
    path: '*',
    redirect: '/',
  },
];

if (authenticationRequired && authenticationRequired === 'true') {
  const login_route = {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { noAuth: true },
  };
  const login_callback_route = {
    path: '/callback',
    name: 'LoginCallback',
    component: LoginCallback,
    meta: { noAuth: true },
  };
  routes.push(login_route);
  routes.push(login_callback_route);
}

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export const loginGuard = () => (to, from, next) => {
  if (authenticationRequired && authenticationRequired === 'false') {
    Store.commit('update_source_route', from.fullPath);
    Store.commit('update_destination_route', to.fullPath);
    Store.commit('update_auth_tokens', null);
    Store.commit('update_user_details', null);
    return next();
  } else if (authenticationRequired && authenticationRequired === 'true') {
    if (to.matched.some((record) => record.meta.noAuth)) {
      return next();
    } else {
      (async () => {
        const isAuthenticated = await AuthService.isUserAuthenticated();
        Store.commit('update_source_route', from.fullPath);
        Store.commit('update_destination_route', to.fullPath);
        if (!isAuthenticated) {
          Store.commit('update_auth_tokens', null);
          Store.commit('update_user_details', null);
          return next({
            path: '/login',
          });
        }
        return next();
      })();
    }
  } else {
    console.log('Invalid value provided for VUE_APP_AUTHENTICATION_REQUIRED env variable');
  }
};

router.beforeEach(loginGuard());

export default router;
