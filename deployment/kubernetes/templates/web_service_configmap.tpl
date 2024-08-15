{{- define "resc.webServiceConfigmapTemplate" -}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Values.global.appName }}-web-service-config{{ .Values.nameSuffix }}
  namespace: {{ .Values.global.namespace }}
  labels:
    app: {{ .Values.global.appName }}
data:
  {{ if .Values.global.enableRedisCache }}
  RESC_REDIS_CACHE_ENABLE: {{ .Values.global.enableRedisCache | quote}}
  {{ end }}
  {{ if .Values.resc.authRequired }}
  AUTHENTICATION_REQUIRED: {{ .Values.resc.authRequired | quote }}
  {{ else }}
  AUTHENTICATION_REQUIRED: {{ .Values.global.authenticationEnabled | quote }}
  {{ end }}
  {{ if .Values.resc.config.dbSchema }}
  MSSQL_SCHEMA: {{ .Values.resc.config.dbSchema }}
  {{ end }}
  {{ if .Values.resc.enableCORS }}
  ENABLE_CORS: {{ .Values.resc.enableCORS | quote }}
  {{ end }}
  {{ if .Values.resc.ssoConfig.ssoAccessTokenIssuerUrl }}
  SSO_ACCESS_TOKEN_ISSUER_URL: {{ .Values.resc.ssoConfig.ssoAccessTokenIssuerUrl }}
  {{ end }}
  {{ if .Values.resc.ssoConfig.ssoAccessTokenJwksUrl }}
  SSO_ACCESS_TOKEN_JWKS_URL: {{ .Values.resc.ssoConfig.ssoAccessTokenJwksUrl }}
  {{ end }}
  {{ if .Values.resc.ssoConfig.ssoJwtSignAlgorithm }}
  SSO_JWT_SIGN_ALGORITHM: {{ .Values.resc.ssoConfig.ssoJwtSignAlgorithm }}
  {{ end }}
  {{ if .Values.resc.ssoConfig.ssoJwtRequiredClaims }}
  SSO_JWT_REQUIRED_CLAIMS: {{ .Values.resc.ssoConfig.ssoJwtRequiredClaims }}
  {{ end }}
  {{ if .Values.resc.ssoConfig.ssoJwtClaimAudience }}
  SSO_JWT_CLAIM_AUDIENCE: {{ .Values.resc.ssoConfig.ssoJwtClaimAudience }}
  {{ end }}
  {{ if .Values.resc.ssoConfig.ssoJwtClaimKeyUserId }}
  SSO_JWT_CLAIM_KEY_USER_ID: {{ .Values.resc.ssoConfig.ssoJwtClaimKeyUserId }}
  {{ end }}
  {{ if .Values.resc.ssoConfig.ssoJwtClaimKeyAuthorization }}
  SSO_JWT_CLAIM_KEY_AUTHORIZATION: {{ .Values.resc.ssoConfig.ssoJwtClaimKeyAuthorization }}
  {{ end }}
  {{ if .Values.resc.ssoConfig.ssoJwtClaimValueAuthorization }}
  SSO_JWT_CLAIM_VALUE_AUTHORIZATION: {{ .Values.resc.ssoConfig.ssoJwtClaimValueAuthorization }}
  {{ end }}
  {{ if .Values.resc.corsAllowedDomains }}
  CORS_ALLOWED_DOMAINS: {{ .Values.resc.corsAllowedDomains }}
  {{ end }}
  {{ if .Values.resc.config.dbPort }}
  MSSQL_DB_PORT: "{{ .Values.resc.config.dbPort }}"
  {{ end }}
  {{ if .Values.resc.config.dbUser }}
  MSSQL_USERNAME: {{ .Values.resc.config.dbUser }}
  {{ end }}
  {{ if .Values.resc.config.odbcDriver }}
  MSSQL_ODBC_DRIVER: {{ .Values.resc.config.odbcDriver }}
  {{ end }}
  {{ if .Values.resc.config.dbHost }}
  MSSQL_DB_HOST: {{ .Values.resc.config.dbHost }}
  {{ end }}
  {{ if .Values.resc.config.dbDSN }}
  MSSQL_DSN: {{ .Values.resc.config.dbDSN }}
  {{ end }}
  {{ if .Values.resc.config.dbUseAzureTokenAuth }}
  DB_USE_AZURE_TOKEN_AUTH: "{{ .Values.resc.config.dbUseAzureTokenAuth }}"
  {{ end }}
  {{ if .Values.resc.config.dbManagedIdentityClientId }}
  MANAGED_IDENTITY_CLIENT_ID: {{ .Values.resc.config.dbManagedIdentityClientId }}
  {{ end }}
  odbc.ini: |
    [{{ .Values.resc.config.dbDSN }}]    
    Driver = {{ .Values.resc.config.odbcDriver }}
    Server = tcp:{{ .Values.resc.config.dbHost }},{{ .Values.resc.config.dbPort }}
{{- end }}