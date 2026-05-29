# Diff Output Formats Reference

## Unified Diff (default)

The most common format. Shows changes with surrounding context lines.

```diff
--- a/src/auth/login.ts
+++ b/src/auth/login.ts
@@ -10,7 +10,8 @@ export class AuthService {
   async login(email: string, password: string): Promise<User> {
     const user = await this.userRepo.findByEmail(email);
-    if (!user) throw new Error('User not found');
+    if (!user) throw new NotFoundError('User not found');
+    if (!user.isActive) throw new ForbiddenError('Account disabled');

     const valid = await bcrypt.compare(password, user.hashedPassword);
     if (!valid) throw new Error('Invalid password');
```

**Key symbols:**
- `---` / `+++` -- file paths (a = old, b = new)
- `@@ -10,7 +10,8 @@` -- hunk header: old file starts at line 10 (7 lines), new file starts at line 10 (8 lines)
- ` ` (space) -- unchanged context line
- `-` -- removed line
- `+` -- added line

## Context Diff

Shows changes with more surrounding lines and uses markers instead of +/-.

```diff
*** a/src/auth/login.ts
--- b/src/auth/login.ts
***************
*** 10,16 ****
   async login(email: string, password: string): Promise<User> {
     const user = await this.userRepo.findByEmail(email);
!    if (!user) throw new Error('User not found');

     const valid = await bcrypt.compare(password, user.hashedPassword);
--- 10,17 ----
   async login(email: string, password: string): Promise<User> {
     const user = await this.userRepo.findByEmail(email);
!    if (!user) throw new NotFoundError('User not found');
!    if (!user.isActive) throw new ForbiddenError('Account disabled');

     const valid = await bcrypt.compare(password, user.hashedPassword);
```

**Key symbols:**
- `!` -- changed line
- `-` -- removed line (in old)
- `+` -- added line (in new)

## Stat Diff

High-level summary of changes per file. Useful for quick overviews.

```diff
 src/auth/login.ts    | 6 ++++--
 src/auth/register.ts | 3 ++-
 src/utils/errors.ts  | 8 ++++++++
 tests/auth.test.ts   | 5 +++++
 4 files changed, 18 insertions(+), 4 deletions(-)
```

**Reading the numbers:**
- `6 ++++--` -- 6 lines changed: 4 added, 2 removed
- `4 files changed, 18 insertions(+), 4 deletions(-)` -- total summary

## Shortstat

One-line summary only.

```
4 files changed, 18 insertions(+), 4 deletions(-)
```

## Numstat

Machine-readable numeric format.

```
4	2	src/auth/login.ts
2	1	src/auth/register.ts
8	0	src/utils/errors.ts
5	0	tests/auth.test.ts
```

Format: `lines_added	lines_removed	filename`

## Name-only / Name-status

Lists only affected filenames or filenames with status.

```
# Name-only
src/auth/login.ts
src/auth/register.ts

# Name-status
M	src/auth/login.ts
M	src/auth/register.ts
A	src/utils/errors.ts
D	src/old-handler.ts
R095	src/renamed.ts	src/new-name.ts
```

Status codes: `A` = added, `D` = deleted, `M` = modified, `R` = renamed (number = similarity %), `C` = copied.

## Word Diff

Highlights changes within a line rather than showing full line replacements.

```diff
This is [-old-]{+new+} text in the [-same-]{+modified+} line.
```

Useful for prose/documentation changes where full-line diffs are hard to read.

## Choosing the Right Format for Analysis

| Use case | Recommended format |
|---|---|
| Detailed code review | Unified diff |
| Quick overview of scope | Stat diff |
| Comparing many files | Numstat + selective unified |
| Documentation/prose changes | Word diff |
| Binary file changes | Name-status |
| Generating change summaries | Shortstat or numstat |
