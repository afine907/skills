# JWT Best Practices

## Token Structure

A JWT consists of three Base64URL-encoded parts: header, payload, and signature.

```
eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature
```

### Header

```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-2024-01"
}
```

### Payload (Claims)

```json
{
  "sub": "user-123",
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com",
  "exp": 1700000000,
  "iat": 1699996400,
  "nbf": 1699996400,
  "jti": "unique-token-id",
  "scope": "read write",
  "roles": ["user", "admin"]
}
```

## Algorithm Selection

| Algorithm | Type | Use Case |
|-----------|------|----------|
| RS256 | Asymmetric | Most web apps, auth server signs, any service verifies |
| ES256 | Asymmetric | Smaller tokens, mobile, IoT |
| EdDSA | Asymmetric | Modern apps, best performance |
| HS256 | Symmetric | Single-service, internal APIs only |

**Never use**: `none`, `HS256` with a public/shared secret.

## Security Rules

### 1. Always Validate All Claims

```python
import jwt

def verify_token(token: str) -> dict:
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience="https://api.example.com",
        issuer="https://auth.example.com",
        options={
            "require": ["exp", "iss", "aud", "sub"],
            "verify_exp": True,
            "verify_iss": True,
            "verify_aud": True,
        },
    )
```

### 2. Keep Tokens Short-Lived

| Token Type | Recommended Lifetime |
|------------|---------------------|
| Access Token | 5-15 minutes |
| Refresh Token | 1-7 days |
| ID Token | 5-15 minutes |

### 3. Use Asymmetric Keys for Distributed Systems

- Auth server holds the private key
- Resource servers only need the public key
- Rotate keys using `kid` (Key ID) in the header
- Publish public keys at `/.well-known/jwks.json`

### 4. Store Tokens Securely

| Storage | XSS Risk | CSRF Risk | Recommendation |
|---------|----------|-----------|----------------|
| localStorage | High | Low | Avoid for sensitive apps |
| sessionStorage | Medium | Low | Better, but still vulnerable |
| HttpOnly cookie | None | Mitigate with SameSite | Recommended |
| Memory variable | None | Low | Best for SPAs with BFF |

### 5. Implement Token Refresh

```
Client                          Auth Server
  |                                  |
  |-- POST /token (refresh_token) -->|
  |<-- { access_token, refresh_token }|
  |                                  |
  |  (old refresh token is now       |
  |   single-use and rotated)        |
```

### 6. Blacklist/Revoke on Logout

```python
# Add token JTI to a blocklist with TTL matching token expiry
def revoke_token(token: str):
    claims = jwt.decode(token, options={"verify_signature": False})
    ttl = claims["exp"] - int(time.time())
    redis.setex(f"blocklist:{claims['jti']}", ttl, "revoked")

def is_revoked(jti: str) -> bool:
    return redis.exists(f"blocklist:{jti}") > 0
```

## Common Vulnerabilities

| Vulnerability | Mitigation |
|---------------|------------|
| Algorithm confusion (`HS256` vs `RS256`) | Explicitly whitelist allowed algorithms |
| Missing signature verification | Always verify signature before using claims |
| Token in URL | Never pass JWTs in query strings |
| Sensitive data in payload | JWTs are Base64-encoded, not encrypted |
| No expiration | Always set `exp` claim |

## Key Rotation Strategy

1. Generate a new key pair with a new `kid`
2. Publish both old and new public keys in JWKS
3. Sign new tokens with the new private key
4. After grace period, remove old key from JWKS
5. Old tokens remain valid until they expire naturally
