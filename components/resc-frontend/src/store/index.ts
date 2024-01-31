import type { RulePackRead } from '@/services/shema-to-types';
import { defineStore, type Store } from 'pinia';

export type TokenData = {
  id_token: string;
  access_token: string;
};

export type UserDetails = {
  firstName: string;
  lastName: string;
  email: string;
};

interface ActionsStore {
  update_auth_tokens: (tokenData: TokenData | null) => void;
  update_source_route: (sourceRoute: string | null) => void;
  update_destination_route: (destinationRoute: string | null) => void;
  update_user_details: (userDetails: UserDetails | null) => void;
  update_previous_route_state: (previousRouteState: string | null | PreviousRouteState) => void;
}

export type PreviousRouteState = {
  ruleName: string;
  rulePackVersions?: RulePackRead[];
  ruleTags?: string[];
};

interface State {
  idToken: null | string;
  accessToken: null | string;
  sourceRoute: null | string;
  destinationRoute: null | string;
  firstName: null | string;
  lastName: null | string;
  email: null | string;
  previousRouteState: null | string | PreviousRouteState;
}

// @ts-expect-error
export const useAuthUserStore: () => Store<'authUser', State, {}, ActionsStore> = defineStore(
  'authUser',
  {
    state: (): State => ({
      idToken: null,
      accessToken: null,
      sourceRoute: null,
      destinationRoute: null,
      firstName: null,
      lastName: null,
      email: null,
      previousRouteState: null,
    }),
    // If extra getters are needed.
    getters: {},
    actions: {
      update_auth_tokens(tokenData: TokenData | null) {
        this.idToken = tokenData?.id_token ?? null;
        this.accessToken = tokenData?.access_token ?? null;
      },
      update_source_route(sourceRoute: string | null) {
        this.sourceRoute = sourceRoute;
      },
      update_destination_route(destinationRoute: string | null) {
        this.destinationRoute = destinationRoute;
      },
      update_user_details(userDetails: UserDetails | null) {
        this.firstName = userDetails?.firstName ?? null;
        this.lastName = userDetails?.lastName ?? null;
        this.email = userDetails?.email ?? null;
      },
      update_previous_route_state(previousRouteState: string | null | PreviousRouteState) {
        this.previousRouteState = previousRouteState;
      },
    },
    modules: {},
    persist: true,
  }
);
