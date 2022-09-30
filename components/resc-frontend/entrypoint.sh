#!/bin/sh

# Replace env vars in JavaScript files
echo "Replacing env vars in JS"
FILES=`find /app -type f \( -iname "*.js*" -not -iname "*.spec.js" \) `
for file in $FILES
do
  echo "Processing $file ...";

  # Use the existing JS file as template
  if [ ! -f $file.tmpl.js ]; then
    cp $file $file.tmpl.js
  fi

  envsubst '$VUE_APP_SSO_JWT_SIGNING_ALOGORITHM,$VUE_APP_SSO_CODE_CHALLENGE_METHOD,$VUE_APP_AUTHENTICATION_REQUIRED,$VUE_APP_RESC_WEB_SERVICE_URL,$VUE_APP_SSO_REDIRECT_URI,$VUE_APP_SSO_ID_TOKEN_ISSUER_URL,$VUE_APP_SSO_AUTHORIZATION_URL,$VUE_APP_SSO_TOKEN_ENDPOINT_URL,$VUE_APP_SSO_ID_TOKEN_JWKS_URL,$VUE_APP_SSO_ACCESS_TOKEN_JWKS_URL' < $file.tmpl.js > $file
done

/docker-entrypoint.sh "$@"
nginx -g 'daemon off;'