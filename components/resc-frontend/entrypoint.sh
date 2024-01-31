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

  envsubst '$VITE_SSO_LOGIN_PAGE_MESSAGE,$VITE_SSO_JWT_SIGNING_ALOGORITHM,$VITE_SSO_CODE_CHALLENGE_METHOD,$VITE_AUTHENTICATION_REQUIRED,$VITE_RESC_WEB_SERVICE_URL,$VITE_SSO_REDIRECT_URI,$VITE_SSO_ID_TOKEN_ISSUER_URL,$VITE_SSO_AUTHORIZATION_URL,$VITE_SSO_TOKEN_ENDPOINT_URL,$VITE_SSO_ID_TOKEN_JWKS_URL,$VITE_SSO_ACCESS_TOKEN_JWKS_URL' < $file.tmpl.js > $file
done

/docker-entrypoint.sh "$@"
nginx -g 'daemon off;'