import axios from 'axios';
import { describe, expect, it, vi } from 'vitest';
import AuthService from '@/services/auth-service';
import { useAuthUserStore } from '@/store/index';
import { setActivePinia, createPinia } from 'pinia';
import * as jose from 'jose';

vi.mock('jose');
vi.mock('axios');

describe('function generateCodeVerifier', () => {
  it('fetch a base64 encoded code verifier', async () => {
    const codeVerifier = AuthService.generateCodeVerifier();
    expect(codeVerifier).toBeDefined();
    expect(codeVerifier.length).toBeGreaterThanOrEqual(43);
    expect(codeVerifier.length).toBeLessThanOrEqual(120);
  });
});

describe('function generateCodeChallenge', () => {
  it('fetch a base64 encoded code challenge', async () => {
    const input = Buffer.from('Hello World');
    const codeVerifier = AuthService.generateCodeChallenge(input);
    expect(codeVerifier).toBeDefined();
    expect(codeVerifier.length).toBe(43);
  });
});

describe('function getCodeVerifier', () => {
  it('fetch a code verifier from local storage', async () => {
    const input = 'mock_code_verifier';
    const getItem = vi.spyOn(Storage.prototype, 'getItem');
    getItem.mockReturnValue(input);
    const codeVerifier = AuthService.getCodeVerifier(input);
    expect(codeVerifier).toBe(input);
  });
});

describe('function setCodeVerifier', () => {
  it('set code_verifier in local storage', async () => {
    const setItem = vi.spyOn(Storage.prototype, 'setItem');
    const input = 'testvalue';
    AuthService.setCodeVerifier(input);
    expect(setItem).toHaveBeenCalledWith('code_verifier', input);
  });
});

describe('function removeCodeVerifier', () => {
  it('remove code_verifier from local storage', async () => {
    const removeItem = vi.spyOn(Storage.prototype, 'removeItem');
    AuthService.removeCodeVerifier();
    expect(removeItem).toHaveBeenCalledWith('code_verifier');
  });
});

describe('function requestLoginPage', () => {
  it('redirect browser to pingfederate sso', async () => {
    const location = new URL('https://www.example.com');
    location.assign = vi.fn();
    location.replace = vi.fn();
    location.reload = vi.fn();

    delete window.location;
    window.location = location;

    AuthService.generateCodeChallenge = vi.fn().mockReturnValue('mockcodechalange');
    const expected_url =
      'https://fake-sso-url/as/authorization.oauth2?response_type=code&scope=openid%20profile%20email&client_id=RESC&code_challenge_method=fake-code-challenge-method&code_challenge=mockcodechalange&redirect_uri=http://localhost:8080/callback';
    AuthService.requestLoginPage();
    expect(window.location.replace).toHaveBeenCalledWith(expected_url);
  });
});

describe('function getAuthTokens', () => {
  it('get auth token', async () => {
    axios.post.mockResolvedValueOnce('fake-auth-token');
    const response = await AuthService.getAuthTokens('data');

    expect(response).toBeDefined();
    expect(response).not.toBeNull();
    expect(response).toEqual('fake-auth-token');
  });
});

describe('function isValidJwtToken', () => {
  it('verify if jwt token is valid or not', async () => {
    const jwtToken = 'fake-token';
    const jwksUrl = 'http://fake-jwks-url';
    const issuerUrl = 'fake-issuer-url';
    vi.spyOn(jose, 'createRemoteJWKSet').mockImplementation(() => jwksUrl);
    jose.jwtVerify.mockResolvedValue(true);
    return AuthService.isValidJwtToken(jwtToken, jwksUrl, issuerUrl).then((data) =>
      expect(data).toEqual(true)
    );
  });
});

describe('function isUserAuthenticated', () => {
  beforeEach(() => {
    // creates a fresh pinia and makes it active
    // so it's automatically picked up by any useStore() call
    // without having to pass it to it: `useStore(pinia)`
    setActivePinia(createPinia());
    const store = useAuthUserStore();
    store.$patch({ idToken: 'fake-id-token' });
  });

  it('verify if user is authenticated or not', async () => {
    const claims = {
      sub: 't12345',
      aud: 'RESC',
      iss: 'https://example.com',
      exp: 1654703824,
      given_name: 'John',
      family_name: 'Doe',
      email: 'johndoe@example.com',
    };
    jose.decodeJwt.mockResolvedValue(claims);
    AuthService.isTokenExpired = vi.fn().mockReturnValue(false);
    AuthService.isValidJwtToken = vi.fn().mockResolvedValue(true);
    return AuthService.isUserAuthenticated().then((data) => expect(data).toEqual(true));
  });
});

describe('function isUserAuthorized', () => {
  it('verify if user is authorized or not', async () => {
    axios.get.mockImplementation(() => Promise.resolve({ status: 200, data: { message: 'OK' } }));
    return AuthService.isUserAuthorized().then((data) => expect(data).toEqual(true));
  });
});

describe('function doAuthCheck', () => {
  it('verify if user has active session or not', async () => {
    const resp = { message: 'OK' };
    axios.get.mockResolvedValue(resp);
    return AuthService.doAuthCheck().then((data) => expect(data).toEqual(resp));
  });
});

describe('function isTokenExpired', () => {
  beforeEach(() => {
    // creates a fresh pinia and makes it active
    // so it's automatically picked up by any useStore() call
    // without having to pass it to it: `useStore(pinia)`
    setActivePinia(createPinia());
    const store = useAuthUserStore();
    store.$patch({ idToken: 'fake-id-token' });
  });

  it('verify if jwt token is valid or not', async () => {
    const claims = {
      sub: 't12345',
      aud: 'RESC',
      iss: 'https://example.com',
      exp: 1654703824,
      given_name: 'John',
      family_name: 'Doe',
      email: 'johndoe@example.com',
    };
    jose.decodeJwt.mockResolvedValue(claims);
    const store = useAuthUserStore();
    const isTokenExpired = AuthService.isTokenExpired(store.idToken);
    expect(isTokenExpired).toBe(false);
  });
});

describe('function getLoggedInUserDetails', () => {
  it('get logged in user details', async () => {
    const claims = {
      sub: 't12345',
      aud: 'RESC',
      iss: 'https://example.com',
      exp: 1654703824,
      given_name: 'John',
      family_name: 'Doe',
      email: 'johndoe@example.com',
    };
    jose.decodeJwt.mockResolvedValue(claims);
    const userDetails = AuthService.getLoggedInUserDetails();
    expect(userDetails.toBeDefined);
  });
});
