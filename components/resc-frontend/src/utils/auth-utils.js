const crypto = require('crypto');

const AuthUtils = {
  base64URLEncode(buffer) {
    return buffer.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  },

  sha256(buffer) {
    return crypto.createHash('sha256').update(buffer).digest();
  },

  parseJwtTokenErrors(errorCode) {
    switch (errorCode) {
      case 'ERR_JWT_INVALID':
        console.error('JWT is invalid');
        break;
      case 'ERR_JWT_EXPIRED':
        console.error('JWT has expired');
        break;
      case 'ERR_JWT_CLAIM_VALIDATION_FAILED':
        console.error('JWT claim validation failed');
        break;
      case 'ERR_JWS_SIGNATURE_VERIFICATION_FAILED':
        console.error('JWS signature verification failed');
        break;
      case 'ERR_JWS_INVALID':
        console.error('JWS is invalid');
        break;
      case 'ERR_JWKS_TIMEOUT':
        console.error('Timeout was reached when retrieving the JWKS response');
        break;
      case 'ERR_JWKS_NO_MATCHING_KEY':
        console.error('No applicable key found in the JSON Web Key Set');
        break;
      case 'ERR_JWKS_MULTIPLE_MATCHING_KEYS':
        console.error('Multiple matching keys found in the JSON Web Key Set');
        break;
      case 'ERR_JWKS_INVALID':
        console.error('JWKS is invalid');
        break;
      case 'ERR_JWK_INVALID':
        console.error('JWK is invalid');
        break;
      case 'ERR_JWE_INVALID':
        console.error('JWE is invalid');
        break;
      case 'ERR_JWE_DECRYPTION_FAILED':
        console.error('JWE ciphertext decryption failed');
        break;
      case 'ERR_JOSE_NOT_SUPPORTED':
        console.error('Algorithm is not supported');
        break;
      case 'ERR_JOSE_ALG_NOT_ALLOWED':
        console.error('Algorithm is not allowed');
        break;
      case 'ERR_JOSE_GENERIC':
        console.error('An error occurred');
        break;
      default:
        console.error('An unexpected error occurred');
        break;
    }
  },
};

export default AuthUtils;
