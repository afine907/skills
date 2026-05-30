# OAuth 2.0 Flows Reference

## Flow Selection Guide

```
Is the client a public app (SPA, mobile, CLI)?
├── Yes → Do you need user consent?
│   ├── Yes → Authorization Code + PKCE
│   └── No  → Device Authorization (for devices without browser)
└── No (server-side app)
    ├── Do you need user consent?
    │   ├── Yes → Authorization Code (with client secret)
    │   └── No  → Client Credentials
    └── Is it a legacy first-party app?
        └── Yes → Resource Owner Password (deprecated, avoid)
```

## 1. Authorization Code + PKCE (Recommended)

Best for: SPAs, mobile apps, single-page applications.

```
User                  Client                Auth Server
  |                      |                       |
  |--- click login ----->|                       |
  |                      |-- redirect with ------>|
  |                      |   code_challenge       |
  |<-- login page -------|                       |
  |--- enter creds ----->|                       |
  |<-- redirect + code --|                       |
  |                      |-- exchange code ------>|
  |                      |   + code_verifier      |
  |                      |<-- access_token -------|
```

### Client-Side Implementation

```typescript
// Step 1: Generate PKCE challenge
function generatePKCE() {
  const verifier = generateRandomString(128);
  const challenge = base64urlencode(sha256(verifier));
  return { verifier, challenge };
}

// Step 2: Authorization request
const authUrl = new URL(AUTH_SERVER + '/authorize');
authUrl.searchParams.set('response_type', 'code');
authUrl.searchParams.set('client_id', CLIENT_ID);
authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
authUrl.searchParams.set('scope', 'openid profile email');
authUrl.searchParams.set('code_challenge', challenge);
authUrl.searchParams.set('code_challenge_method', 'S256');
authUrl.searchParams.set('state', randomState);

// Step 3: Token exchange
const response = await fetch(AUTH_SERVER + '/token', {
  method: 'POST',
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: authorizationCode,
    redirect_uri: REDIRECT_URI,
    client_id: CLIENT_ID,
    code_verifier: storedVerifier,
  }),
});
```

## 2. Client Credentials

Best for: Machine-to-machine, service-to-service, CLI tools.

```
Service               Auth Server
  |                        |
  |-- POST /token -------->|
  |   grant_type=client_   |
  |   credentials          |
  |   client_id + secret   |
  |<-- access_token --------|
```

### Implementation

```python
import httpx

async def get_service_token() -> str:
    response = await httpx.post(
        f"{AUTH_SERVER}/token",
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "api:read api:write",
        },
    )
    return response.json()["access_token"]
```

## 3. Device Authorization

Best for: Smart TVs, CLI tools, IoT devices without browsers.

```
Device                Auth Server              User (separate device)
  |                        |                          |
  |-- POST /device ------>|                          |
  |<-- device_code +      |                          |
  |    user_code +        |                          |
  |    verification_uri   |                          |
  |                       |                          |
  |  (polling)            |                          |
  |-- POST /token ------->|                          |
  |   device_code         |                          |
  |<-- 400 pending -------|                          |
  |                       |<-- user visits URI ------|
  |                       |    enters user_code      |
  |                       |    authorizes -----------|
  |-- POST /token ------->|                          |
  |<-- access_token ------|                          |
```

## 4. Refresh Token Flow

```typescript
async function refreshAccessToken(refreshToken: string): Promise<TokenResponse> {
  const response = await fetch(AUTH_SERVER + '/token', {
    method: 'POST',
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: CLIENT_ID,
    }),
  });

  if (!response.ok) {
    throw new TokenExpiredError();
  }

  return response.json(); // new access_token + possibly new refresh_token
}
```

## Token Types

| Token | Purpose | Lifetime | Storage |
|-------|---------|----------|---------|
| Access Token | API authorization | 5-60 min | Memory or HttpOnly cookie |
| Refresh Token | Get new access tokens | 1-90 days | HttpOnly cookie, secure storage |
| ID Token (OIDC) | User identity claims | 5-60 min | Memory only |

## Scopes

| Scope | Access Granted |
|-------|---------------|
| `openid` | User identifier (sub claim) |
| `profile` | Name, picture, etc. |
| `email` | Email address |
| `offline_access` | Refresh token |
| Custom scopes | Application-defined API permissions |

## Security Checklist

- [ ] Always use HTTPS for redirect URIs
- [ ] Validate `state` parameter to prevent CSRF
- [ ] Use PKCE for all public clients
- [ ] Validate `iss`, `aud`, `exp` on received tokens
- [ ] Store client secrets securely (never in client-side code)
- [ ] Rotate client secrets periodically
- [ ] Implement token revocation endpoint
- [ ] Log authentication events for audit
- [ ] Rate-limit token endpoint
