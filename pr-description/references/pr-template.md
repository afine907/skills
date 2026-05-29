# PR Description Template Reference

## Standard Template

```markdown
## Summary

Brief description of what this PR does and why. Link to relevant issue(s).

Closes #123

## Changes

- Added user authentication middleware to validate JWT tokens
- Updated login endpoint to return refresh tokens
- Fixed token expiration check that was using wrong timezone

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Refactor (no functional changes)
- [ ] Documentation update
- [ ] Test improvement

## Screenshots / Recordings

<!-- If applicable, add screenshots or recordings showing the change -->

## Testing

Describe how the changes were tested:

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

**Test instructions:**
1. Run `npm test`
2. Navigate to /login
3. Try logging in with expired token
4. Verify refresh token is returned

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-reviewed the code
- [ ] Comments added for complex logic
- [ ] Documentation updated if needed
- [ ] No new warnings introduced
- [ ] Tests pass locally

## Deployment Notes

<!-- Any special deployment steps, environment variables, migrations, etc. -->

- Requires running `npm run migrate` before deployment
- New env var: `JWT_REFRESH_SECRET` must be set
```

---

## Minimal Template (for small changes)

```markdown
## What

One-line description of the change.

## Why

One-line reason for the change.

## Testing

How it was verified.
```

---

## Bug Fix Template

```markdown
## Bug

**What was happening:** Users got a 500 error when uploading files larger than 10MB.

**Root cause:** The request body parser had a 10MB default limit that wasn't configured.

**Fix:** Increased the limit to 50MB and added proper error handling for oversized uploads.

Closes #456

## Verification

- Tested with 5MB file (passes)
- Tested with 49MB file (passes)
- Tested with 51MB file (returns 413 with clear error message)
- Added unit test for the size limit
```

---

## Feature Template

```markdown
## Feature

Add dark mode support to the settings page.

## Motivation

Users requested dark mode to reduce eye strain during nighttime usage. See #789.

## Implementation

- Added `ThemeProvider` context wrapping the app
- Created dark/light color token sets in `theme/tokens.ts`
- Added toggle in Settings with localStorage persistence
- Updated 12 components to use theme tokens instead of hardcoded colors

## Preview

<!-- Add before/after screenshots -->

## Rollout

- Behind `FF_DARK_MODE` feature flag (currently 10% of users)
- No database migration needed
```

---

## Refactor Template

```markdown
## Refactor

Extract authentication logic from route handlers into a dedicated middleware.

## Motivation

Auth checks are duplicated across 15 route handlers, making it hard to update
the auth flow consistently. Some handlers skip important checks.

## What Changed

- Created `middleware/auth.ts` with `requireAuth` and `requireRole` middleware
- Removed duplicate auth logic from all route handlers
- Added `requireRole('admin')` to admin-only routes
- No behavioral change -- all tests pass as-is

## Risk Assessment

Low risk -- this is a pure refactor with no functional changes. All existing
tests pass without modification.
```

---

## Key Principles

1. **Lead with why** -- reviewers need context before code details
2. **Link issues** -- always reference related tickets
3. **Be specific about testing** -- "tested locally" is not enough
4. **Flag breaking changes** -- make them obvious
5. **Include deployment notes** -- migrations, env vars, feature flags
6. **Keep it scannable** -- use headers, bullet points, and checklists
