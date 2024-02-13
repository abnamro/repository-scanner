import AuthUtils from '@/utils/auth-utils';
import AxiosConfig from '@/configuration/axios-config';
import Router from '@/router/index';
import { useAuthUserStore, type UserDetails } from '@/store/index';
import Config from '@/configuration/config';
import axiosRetry from 'axios-retry';

import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios';
axiosRetry(axios, { retries: 3 });
import crypto from 'crypto';
import qs from 'qs';
import * as jose from 'jose';

export type OauthToken = {
  id_token: string;
  access_token: string;
};

const AuthService = {
  generateCodeVerifier(): string {
    return AuthUtils.base64URLEncode(crypto.randomBytes(60));
  },

  generateCodeChallenge(verifier: string): string {
    return AuthUtils.base64URLEncode(AuthUtils.sha256(verifier as unknown as Buffer));
  },

  getAuthCode(): string | null | undefined {
    const params = new URLSearchParams(window.location.search);
    if (params.has('code')) {
      return params.get('code');
    }
  },

  getCodeVerifier(): string | null {
    return localStorage.getItem('code_verifier');
  },

  setCodeVerifier(verifier: string): void {
    localStorage.setItem('code_verifier', verifier);
  },

  removeCodeVerifier(): void {
    localStorage.removeItem('code_verifier');
  },

  requestLoginPage(): void {
    const codeVerifier = this.generateCodeVerifier();
    this.setCodeVerifier(codeVerifier);

    if (codeVerifier) {
      const codeChallenge = this.generateCodeChallenge(codeVerifier);

      const loginUrl = `${Config.value('ssoAuthorizationUrl')}?response_type=${Config.value(
        'ssoResponseType',
      )}&scope=${Config.value('ssoScope')}&client_id=${Config.value(
        'ssoClientId',
      )}&code_challenge_method=${Config.value(
        'ssoCodeChallengeMethod',
      )}&code_challenge=${codeChallenge}&redirect_uri=${Config.value('ssoRedirectUri')}`;

      window.location.replace(encodeURI(loginUrl));
    }
  },

  doLogin(): Promise<AxiosResponse> {
    const authCode = this.getAuthCode(); // window.location.href);
    const codeVerifier = this.getCodeVerifier();
    const store = useAuthUserStore();

    if (authCode && codeVerifier) {
      const data = qs.stringify({
        grant_type: `${Config.value('ssoGrantType')}`,
        client_id: `${Config.value('ssoClientId')}`,
        code: authCode,
        redirect_uri: `${Config.value('ssoRedirectUri')}`,
        code_verifier: codeVerifier,
      });

      return new Promise((resolve, reject) => {
        this.getAuthTokens(data)
          .then((response) => {
            store.update_auth_tokens({
              id_token: response.data.id_token,
              access_token: response.data.access_token,
            });

            (async () => {
              const isAuthorized = await this.isUserAuthorized();
              if (isAuthorized) {
                this.updateUserDetailsInStore();
                if (store.destinationRoute) {
                  Router.push(store.destinationRoute).catch((error) => {
                    AxiosConfig.handleError(error);
                  });
                } else {
                  Router.push('/').catch((error) => {
                    AxiosConfig.handleError(error);
                  });
                }
              } else {
                this.doLogOut();
              }
            })();
            resolve(response);
          })
          .catch((error) => {
            this.doLogOut();
            reject(error);
          })
          .finally(() => {
            this.removeCodeVerifier();
          });
      });
    } else {
      throw new Error('authCode && codeVerifier are null!');
    }
  },

  doLogOut(): void {
    const store = useAuthUserStore();
    store.update_auth_tokens(null);
    store.update_user_details(null);
    store.update_source_route(null);
    store.update_destination_route(null);
    this.removeCodeVerifier();
    Router.push('/login').catch((error) => {
      AxiosConfig.handleError(error);
    });
  },

  async getAuthTokens(data: string): Promise<AxiosResponse<OauthToken>> {
    const config: AxiosRequestConfig<string> = {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    };
    return axios.post(`${Config.value('ssoTokenEndPointUrl')}`, data, config);
  },

  async isValidJwtToken(jwtToken: string, jwksUrl: string, issuerUrl?: string): Promise<boolean> {
    const JWKS = jose.createRemoteJWKSet(new URL(jwksUrl));
    const isValid = await jose
      .jwtVerify(jwtToken, JWKS, {
        issuer: issuerUrl,
        audience: `${Config.value('ssoClientId')}`,
        algorithms: [`${Config.value('ssoJwtSigningAlgorithm')}`],
      })
      .catch((error) => {
        try {
          AuthUtils.parseJwtTokenErrors(error.code);
        } catch (_error) {
          // We silence the error
        }
      });
    return isValid ? true : false;
  },

  async isUserAuthenticated(): Promise<boolean> {
    const store = useAuthUserStore();
    const token = store.idToken;

    if (token && !this.isTokenExpired(token)) {
      const isAuthenticated = await this.isValidJwtToken(
        token,
        `${Config.value('ssoIdTokenJwksUrl')}`,
      );
      return isAuthenticated ? true : false;
    }
    return false;
  },

  async isUserAuthorized(): Promise<boolean> {
    const response = await this.doAuthCheck();
    return response && response.status && response.status === 200 ? true : false;
  },

  async doAuthCheck(): Promise<AxiosResponse<string> | void> {
    return axios.get(`/auth-check`).catch((error) => {
      AxiosConfig.handleError(error);
    });
  },

  getLoggedInUserDetails(): UserDetails | undefined {
    const store = useAuthUserStore();
    if (store.idToken === null) {
      return;
    }

    const claims = jose.decodeJwt(store.idToken);
    return {
      firstName: claims.given_name as string,
      lastName: claims.family_name as string,
      email: claims.email as string,
    };
  },

  isTokenExpired(token: string): boolean {
    try {
      const claims = jose.decodeJwt(token);
      if (claims.exp === undefined) {
        return true;
      }
      return Math.floor(Date.now() / 1000) >= claims.exp ? true : false;
    } catch (_error) {
      return true;
    }
  },

  updateUserDetailsInStore(): void {
    const userDetails = this.getLoggedInUserDetails();
    if (userDetails === undefined) {
      return;
    }

    const store = useAuthUserStore();
    store.update_user_details({
      firstName: userDetails.firstName,
      lastName: userDetails.lastName,
      email: userDetails.email,
    });
  },
};

export default AuthService;
