import dotenv from 'dotenv';
dotenv.config();

export default class Config {
  static get CONFIG() {
    return {
      authenticationRequired: '$VUE_APP_AUTHENTICATION_REQUIRED',
      rescWebServiceUrl: '$VUE_APP_RESC_WEB_SERVICE_URL',
      ssoRedirectUri: '$VUE_APP_SSO_REDIRECT_URI',
      ssoIdTokenIssuerUrl: '$VUE_APP_SSO_ID_TOKEN_ISSUER_URL',
      ssoAuthorizationUrl: '$VUE_APP_SSO_AUTHORIZATION_URL',
      ssoTokenEndPointUrl: '$VUE_APP_SSO_TOKEN_ENDPOINT_URL',
      ssoIdTokenJwksUrl: '$VUE_APP_SSO_ID_TOKEN_JWKS_URL',
      ssoAccessTokenJwksUrl: '$VUE_APP_SSO_ACCESS_TOKEN_JWKS_URL',
      ssoGrantType: 'authorization_code',
      ssoResponseType: 'code',
      ssoScope: 'openid profile email',
      ssoClientId: 'RESC',
      ssoCodeChallengeMethod: '$VUE_APP_SSO_CODE_CHALLENGE_METHOD',
      ssoJwtSigningAlgorithm: '$VUE_APP_SSO_JWT_SIGNING_ALOGORITHM',
      defaultPageSize: '100',
    };
  }

  static value(name) {
    if (!(name in this.CONFIG)) {
      console.log(`Configuration: There is no key named "${name}"`);
      return;
    }

    const value = this.CONFIG[name];

    if (!value) {
      console.log(`Configuration: Value for "${name}" is not defined`);
      return;
    }

    if (value.startsWith('$VUE_APP_')) {
      // value was not replaced, it seems we are in development.
      // Remove $ and get current value from process.env
      const envName = value.substr(1);
      const envValue = process.env[envName];
      if (envValue) {
        return envValue;
      } else {
        console.log(`Configuration: Environment variable "${envName}" is not defined`);
      }
    } else {
      // value was already replaced, it seems we are in production.
      return value;
    }
  }
}
