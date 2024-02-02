import { describe, expect, it } from 'vitest';
import AuthUtils from '@/utils/auth-utils';

describe('function base64URLEncode', () => {
  it('fetch a base64 url encoded string from a buffer', async () => {
    const inputstr = 'https://test.testing/?abc=123&cba=321';
    const input = Buffer.from(inputstr);

    const base64 = AuthUtils.base64URLEncode(input);
    expect(base64).toBeDefined();
    expect(base64).toBe('aHR0cHM6Ly90ZXN0LnRlc3RpbmcvP2FiYz0xMjMmY2JhPTMyMQ');
    expect(Buffer.from(base64, 'base64').toString('ascii')).toBe(inputstr);
  });
});

describe('function sha256', () => {
  it('fetch a sha256 encoded object', async () => {
    const inputstr = 'https://test.testing/?abc=123&cba=321';
    const input = Buffer.from(inputstr);

    const sha256 = AuthUtils.sha256(input);
    expect(sha256).toBeDefined();
    expect(sha256).toHaveLength(32);
  });
});

describe('Unit tests for parseJwtTokenErrors function', () => {
  it('Verify JWT is invalid is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWT_INVALID')).toThrowError('JWT is invalid');
  });
  it('Verify JWT is invalid is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWT_EXPIRED')).toThrowError('JWT has expired');
  });
  it('Verify JWT claim validation failed is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWT_CLAIM_VALIDATION_FAILED')).toThrowError(
      'JWT claim validation failed'
    );
  });
  it('Verify JWS signature verification failed is thrown', async () => {
    expect(() =>
      AuthUtils.parseJwtTokenErrors('ERR_JWS_SIGNATURE_VERIFICATION_FAILED')
    ).toThrowError('JWS signature verification failed');
  });
  it('Verify JWS is invalid is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWS_INVALID')).toThrowError('JWS is invalid');
  });
  it('Verify Timeout was reached when retrieving the JWKS response is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWKS_TIMEOUT')).toThrowError(
      'Timeout was reached when retrieving the JWKS response'
    );
  });
  it('Verify No applicable key found in the JSON Web Key Set is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWKS_NO_MATCHING_KEY')).toThrowError(
      'No applicable key found in the JSON Web Key Set'
    );
  });
  it('Verify Multiple matching keys found in the JSON Web Key Set is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWKS_MULTIPLE_MATCHING_KEYS')).toThrowError(
      'Multiple matching keys found in the JSON Web Key Set'
    );
  });
  it('Verify JWKS is invalid is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWKS_INVALID')).toThrowError('JWKS is invalid');
  });
  it('Verify JWK is invalid is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWK_INVALID')).toThrowError('JWK is invalid');
  });
  it('Verify JWE is invalid is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWE_INVALID')).toThrowError('JWE is invalid');
  });
  it('Verify JWE ciphertext decryption failed is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JWE_DECRYPTION_FAILED')).toThrowError(
      'JWE ciphertext decryption failed'
    );
  });
  it('Verify Algorithm is not supported is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JOSE_NOT_SUPPORTED')).toThrowError(
      'Algorithm is not supported'
    );
  });
  it('Verify Algorithm is not allowed is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JOSE_ALG_NOT_ALLOWED')).toThrowError(
      'Algorithm is not allowed'
    );
  });
  it('Verify An error occurred is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors('ERR_JOSE_GENERIC')).toThrowError(
      'An error occurred'
    );
  });
  it('Verify An unexpected error occurred is thrown', async () => {
    expect(() => AuthUtils.parseJwtTokenErrors()).toThrowError('An unexpected error occurred');
  });
});
