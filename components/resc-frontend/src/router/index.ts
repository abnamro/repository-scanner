import {
  createRouter,
  createWebHistory,
  type NavigationGuardNext,
  type RouteLocationNormalized,
} from 'vue-router';
import Config from '@/configuration/config';
import FindingMetrics from '@/components/Metrics/FindingMetrics.vue';
import AuditMetrics from '@/components/Metrics/AuditMetrics.vue';
import { useAuthUserStore } from '@/store/index';
import Analytics from '@/views/AnalyticsPanel.vue';
import RepositoriesPanel from '@/views/RepositoriesPanel.vue';
import ScanFindings from '@/views/ScanFindings.vue';
import RuleAnalysis from '@/views/RuleAnalysis.vue';
import RulePacks from '@/views/RulePacks.vue';
import RuleMetrics from '@/components/Metrics/RuleMetrics.vue';
import Login from '@/views/LoginPanel.vue';
import LoginCallback from '@/components/Login/LoginCallback.vue';
import AuthService from '@/services/auth-service';

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
    component: RepositoriesPanel,
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
    path: '/:catchAll(.*)',
    redirect: '/',
  },
];

if (authenticationRequired && authenticationRequired === 'true') {
  const loginRoute = {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { noAuth: true },
  };
  const loginCallbackRoute = {
    path: '/callback',
    name: 'LoginCallback',
    component: LoginCallback,
    meta: { noAuth: true },
  };
  routes.push(loginRoute);
  routes.push(loginCallbackRoute);
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export const loginGuard =
  () => (to: RouteLocationNormalized, from: RouteLocationNormalized, next: NavigationGuardNext) => {
    if (authenticationRequired && authenticationRequired === 'false') {
      const store = useAuthUserStore();
      store.update_source_route(from.fullPath);
      store.update_destination_route(to.fullPath);
      store.update_auth_tokens(null);
      store.update_user_details(null);
      return next();
    } else if (authenticationRequired && authenticationRequired === 'true') {
      if (to.matched.some((record) => record.meta.noAuth)) {
        return next();
      } else {
        (async () => {
          const isAuthenticated = await AuthService.isUserAuthenticated();
          const store = useAuthUserStore();
          store.update_source_route(from.fullPath);
          store.update_destination_route(to.fullPath);
          if (!isAuthenticated) {
            store.update_auth_tokens(null);
            store.update_user_details(null);
            return next({
              path: '/login',
            });
          }
          return next();
        })();
      }
    } else {
      throw new Error('Invalid value provided for VITE_AUTHENTICATION_REQUIRED env variable');
    }
  };

router.beforeEach(loginGuard());

export default router;
