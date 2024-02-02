import crypto from 'crypto';

const JwtErrorMsg: { [key: string]: string } = {
  ERR_JWT_INVALID: 'JWT is invalid',
  ERR_JWT_EXPIRED: 'JWT has expired',
  ERR_JWT_CLAIM_VALIDATION_FAILED: 'JWT claim validation failed',
  ERR_JWS_SIGNATURE_VERIFICATION_FAILED: 'JWS signature verification failed',
  ERR_JWS_INVALID: 'JWS is invalid',
  ERR_JWKS_TIMEOUT: 'Timeout was reached when retrieving the JWKS response',
  ERR_JWKS_NO_MATCHING_KEY: 'No applicable key found in the JSON Web Key Set',
  ERR_JWKS_MULTIPLE_MATCHING_KEYS: 'Multiple matching keys found in the JSON Web Key Set',
  ERR_JWKS_INVALID: 'JWKS is invalid',
  ERR_JWK_INVALID: 'JWK is invalid',
  ERR_JWE_INVALID: 'JWE is invalid',
  ERR_JWE_DECRYPTION_FAILED: 'JWE ciphertext decryption failed',
  ERR_JOSE_NOT_SUPPORTED: 'Algorithm is not supported',
  ERR_JOSE_ALG_NOT_ALLOWED: 'Algorithm is not allowed',
  ERR_JOSE_GENERIC: 'An error occurred',
};

const AuthUtils = {
  base64URLEncode(buffer: Buffer): string {
    return buffer.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  },

  sha256(buffer: Buffer): Buffer {
    return crypto.createHash('sha256').update(buffer).digest();
  },

  parseJwtTokenErrors(errorCode: string): void {
    if (errorCode in JwtErrorMsg) {
      throw new Error(JwtErrorMsg[errorCode]);
    }
    throw new Error('An unexpected error occurred');
  },
};

export default AuthUtils;
