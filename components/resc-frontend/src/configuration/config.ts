type ConfigKey =
  | 'authenticationRequired'
  | 'rescWebServiceUrl'
  | 'ssoRedirectUri'
  | 'ssoIdTokenIssuerUrl'
  | 'ssoAuthorizationUrl'
  | 'ssoTokenEndPointUrl'
  | 'ssoIdTokenJwksUrl'
  | 'ssoAccessTokenJwksUrl'
  | 'ssoGrantType'
  | 'ssoResponseType'
  | 'ssoScope'
  | 'ssoClientId'
  | 'ssoCodeChallengeMethod'
  | 'ssoJwtSigningAlgorithm'
  | 'ssoLoginPageMessage'
  | 'defaultPageSize'
  | 'skipRecords'
  | 'limitRecords'
  | 'azureDevOpsVal'
  | 'azureDevOpsLabel'
  | 'bitbucketVal'
  | 'bitbucketLabel'
  | 'githubPublicVal'
  | 'githubPublicLabel'
  | 'notAnalyzedStatusVal'
  | 'notAnalyzedStatusLabel'
  | 'underReviewStatusVal'
  | 'underReviewStatusLabel'
  | 'clarificationRequiredStatusVal'
  | 'clarificationRequiredStatusLabel'
  | 'truePostiveStatusVal'
  | 'truePostiveStatusLabel'
  | 'falsePositiveStatusVal'
  | 'falsePositiveStatusLabel';

export default class Config {
  static get CONFIG() {
    return {
      authenticationRequired: '$VITE_AUTHENTICATION_REQUIRED',
      rescWebServiceUrl: '$VITE_RESC_WEB_SERVICE_URL',
      ssoRedirectUri: '$VITE_SSO_REDIRECT_URI',
      ssoIdTokenIssuerUrl: '$VITE_SSO_ID_TOKEN_ISSUER_URL',
      ssoAuthorizationUrl: '$VITE_SSO_AUTHORIZATION_URL',
      ssoTokenEndPointUrl: '$VITE_SSO_TOKEN_ENDPOINT_URL',
      ssoIdTokenJwksUrl: '$VITE_SSO_ID_TOKEN_JWKS_URL',
      ssoAccessTokenJwksUrl: '$VITE_SSO_ACCESS_TOKEN_JWKS_URL',
      ssoGrantType: 'authorization_code',
      ssoResponseType: 'code',
      ssoScope: 'openid profile email',
      ssoClientId: 'RESC',
      ssoCodeChallengeMethod: '$VITE_SSO_CODE_CHALLENGE_METHOD',
      ssoJwtSigningAlgorithm: '$VITE_SSO_JWT_SIGNING_ALOGORITHM',
      ssoLoginPageMessage: '$VITE_SSO_LOGIN_PAGE_MESSAGE',
      defaultPageSize: '100',
      skipRecords: '0',
      limitRecords: '100',
      azureDevOpsVal: 'AZURE_DEVOPS',
      azureDevOpsLabel: 'Azure DevOps',
      bitbucketVal: 'BITBUCKET',
      bitbucketLabel: 'Bitbucket',
      githubPublicVal: 'GITHUB_PUBLIC',
      githubPublicLabel: 'GitHub Public',
      notAnalyzedStatusVal: 'NOT_ANALYZED',
      notAnalyzedStatusLabel: 'Not Analyzed',
      underReviewStatusVal: 'UNDER_REVIEW',
      underReviewStatusLabel: 'Under Review',
      clarificationRequiredStatusVal: 'CLARIFICATION_REQUIRED',
      clarificationRequiredStatusLabel: 'Clarification Required',
      truePostiveStatusVal: 'TRUE_POSITIVE',
      truePostiveStatusLabel: 'True Positive',
      falsePositiveStatusVal: 'FALSE_POSITIVE',
      falsePositiveStatusLabel: 'False Positive',
    };
  }

  static value(name: ConfigKey): string {
    if (!(name in this.CONFIG)) {
      throw new Error(`Configuration: There is no key named "${name}"`);
    }

    const value = this.CONFIG[name];

    if (!value) {
      throw new Error(`Configuration: Value for "${name}" is not defined`);
    }

    if (value.startsWith('$VITE_')) {
      // value was not replaced, it seems we are in development.
      // Remove $ and get current value from import.meta.env
      const envName = value.substring(1);
      const envValue = import.meta.env[envName] as string;
      if (envValue) {
        return envValue;
      } else {
        throw new Error(`Configuration: Environment variable "${envName}" is not defined`);
      }
    } else {
      // value was already replaced, it seems we are in production.
      return value;
    }
  }
}
