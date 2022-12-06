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
  const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
  beforeEach(() => {
    consoleSpy.mockClear();
  });
  it('Verify JWT is invalid is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWT_INVALID');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWT is invalid');
  });
  it('Verify JWT is invalid is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWT_EXPIRED');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWT has expired');
  });
  it('Verify JWT claim validation failed is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWT_CLAIM_VALIDATION_FAILED');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWT claim validation failed');
  });
  it('Verify JWS signature verification failed is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWS_SIGNATURE_VERIFICATION_FAILED');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWS signature verification failed');
  });
  it('Verify JWS is invalid is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWS_INVALID');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWS is invalid');
  });
  it('Verify Timeout was reached when retrieving the JWKS response is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWKS_TIMEOUT');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith(
      'Timeout was reached when retrieving the JWKS response'
    );
  });
  it('Verify No applicable key found in the JSON Web Key Set is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWKS_NO_MATCHING_KEY');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith(
      'No applicable key found in the JSON Web Key Set'
    );
  });
  it('Verify Multiple matching keys found in the JSON Web Key Set is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWKS_MULTIPLE_MATCHING_KEYS');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith(
      'Multiple matching keys found in the JSON Web Key Set'
    );
  });
  it('Verify JWKS is invalid is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWKS_INVALID');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWKS is invalid');
  });
  it('Verify JWK is invalid is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWK_INVALID');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWK is invalid');
  });
  it('Verify JWE is invalid is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWE_INVALID');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWE is invalid');
  });
  it('Verify JWE ciphertext decryption failed is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JWE_DECRYPTION_FAILED');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('JWE ciphertext decryption failed');
  });
  it('Verify Algorithm is not supported is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JOSE_NOT_SUPPORTED');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('Algorithm is not supported');
  });
  it('Verify Algorithm is not allowed is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JOSE_ALG_NOT_ALLOWED');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('Algorithm is not allowed');
  });
  it('Verify An error occurred is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors('ERR_JOSE_GENERIC');
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('An error occurred');
  });
  it('Verify An unexpected error occurred is printed in console.error', async () => {
    AuthUtils.parseJwtTokenErrors();
    expect(console.error).toBeCalledTimes(1);
    expect(console.error).toHaveBeenLastCalledWith('An unexpected error occurred');
  });
});
