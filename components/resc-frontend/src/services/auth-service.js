import AuthUtils from '@/utils/auth-utils';
import AxiosConfig from '@/configuration/axios-config.js';
import Router from '@/router/index.js';
import Store from '@/store/index.js';
import Config from '@/configuration/config';
import axiosRetry from 'axios-retry';

const axios = require('axios');
axiosRetry(axios, { retries: 3 });
const crypto = require('crypto');
const qs = require('qs');
const jose = require('jose');

const AuthService = {
  generateCodeVerifier() {
    return AuthUtils.base64URLEncode(crypto.randomBytes(60));
  },

  generateCodeChallenge(verifier) {
    return AuthUtils.base64URLEncode(AuthUtils.sha256(verifier));
  },

  getAuthCode() {
    const params = new URLSearchParams(window.location.search);
    if (params.has('code')) {
      return params.get('code');
    }
  },

  getCodeVerifier() {
    return localStorage.getItem('code_verifier');
  },

  setCodeVerifier(verifier) {
    localStorage.setItem('code_verifier', verifier);
  },

  removeCodeVerifier() {
    localStorage.removeItem('code_verifier');
  },

  requestLoginPage() {
    const codeVerifier = this.generateCodeVerifier();
    this.setCodeVerifier(codeVerifier);

    if (codeVerifier) {
      const codeChallenge = this.generateCodeChallenge(codeVerifier);

      const loginUrl = `${Config.value('ssoAuthorizationUrl')}?response_type=${Config.value(
        'ssoResponseType'
      )}&scope=${Config.value('ssoScope')}&client_id=${Config.value(
        'ssoClientId'
      )}&code_challenge_method=${Config.value(
        'ssoCodeChallengeMethod'
      )}&code_challenge=${codeChallenge}&redirect_uri=${Config.value('ssoRedirectUri')}`;

      window.location.replace(encodeURI(loginUrl));
    }
  },

  doLogin() {
    const authCode = this.getAuthCode(window.location.href);
    const codeVerifier = this.getCodeVerifier();

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
            Store.commit('update_auth_tokens', {
              id_token: response.data.id_token,
              access_token: response.data.access_token,
            });

            (async () => {
              const isAuthorized = await this.isUserAuthorized();
              if (isAuthorized) {
                this.updateUserDetailsInStore();
                if (Store.getters.destinationRoute) {
                  Router.push(Store.getters.destinationRoute).catch((error) => {
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
    }
  },

  doLogOut() {
    Store.commit('update_auth_tokens', null);
    Store.commit('update_user_details', null);
    Store.commit('update_source_route', null);
    Store.commit('update_destination_route', null);
    this.removeCodeVerifier();
    Router.push('/login').catch((error) => {
      AxiosConfig.handleError(error);
    });
  },

  async getAuthTokens(data) {
    const headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
    };
    return axios.post(`${Config.value('ssoTokenEndPointUrl')}`, data, headers);
  },

  async isValidJwtToken(jwtToken, jwksUrl, issuerUrl) {
    const JWKS = jose.createRemoteJWKSet(new URL(jwksUrl));
    const isValid = await jose
      .jwtVerify(jwtToken, JWKS, {
        issuer: issuerUrl,
        audience: `${Config.value('ssoClientId')}`,
        algorithms: [`${Config.value('ssoJwtSigningAlgorithm')}`],
      })
      .catch((error) => {
        AuthUtils.parseJwtTokenErrors(error.code);
      });
    return isValid ? true : false;
  },

  async isUserAuthenticated() {
    if (Store.getters.idToken && !this.isTokenExpired(Store.getters.idToken)) {
      const isAuthenticated = await this.isValidJwtToken(
        Store.getters.idToken,
        `${Config.value('ssoIdTokenJwksUrl')}`
      );
      return isAuthenticated ? true : false;
    }
    return false;
  },

  async isUserAuthorized() {
    const response = await this.doAuthCheck();
    return response && response.status && response.status === 200 ? true : false;
  },

  async doAuthCheck() {
    return axios.get(`/auth-check`).catch((error) => {
      AxiosConfig.handleError(error);
    });
  },

  getLoggedInUserDetails() {
    const claims = jose.decodeJwt(Store.getters.idToken);
    return {
      firstName: claims.given_name,
      lastName: claims.family_name,
      email: claims.email,
    };
  },

  isTokenExpired(token) {
    const claims = jose.decodeJwt(token);
    return Math.floor(Date.now() / 1000) >= claims.exp ? true : false;
  },

  updateUserDetailsInStore() {
    const userDetails = this.getLoggedInUserDetails();
    Store.commit('update_user_details', {
      firstName: userDetails.firstName,
      lastName: userDetails.lastName,
      email: userDetails.email,
    });
  },
};

export default AuthService;
