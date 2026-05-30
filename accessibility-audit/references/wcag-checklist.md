# WCAG 2.1 Checklist

Quick-reference checklist for auditing web accessibility against WCAG 2.1 AA criteria.

## Principle 1: Perceivable

### 1.1 Text Alternatives
- [ ] All `<img>` elements have descriptive `alt` text
- [ ] Decorative images use `alt=""` or CSS background
- [ ] Complex images (charts, diagrams) have long descriptions
- [ ] `<svg>` elements have `<title>` and/or `aria-label`
- [ ] `<video>` elements have `<track>` for captions

### 1.2 Time-based Media
- [ ] Pre-recorded audio has transcripts
- [ ] Pre-recorded video has captions (synchronized)
- [ ] Pre-recorded video has audio descriptions for visual content
- [ ] Live audio-only has real-time captions or text alternative

### 1.3 Adaptable
- [ ] Page has one `<h1>` and correct heading hierarchy (no skipped levels)
- [ ] Lists use `<ul>`, `<ol>`, or `<dl>` elements
- [ ] Tables use `<th>` with `scope` attributes
- [ ] Form inputs have associated `<label>` elements
- [ ] Reading order matches visual order in source markup
- [ ] Instructions do not rely solely on shape, size, or position

### 1.4 Distinguishable
- [ ] Text contrast ratio >= 4.5:1 (normal text) or >= 3:1 (large text)
- [ ] Text can be resized to 200% without loss of content
- [ ] Content reflows at 320px width (no horizontal scroll)
- [ ] No information conveyed by color alone
- [ ] Text spacing can be overridden without breaking layout

## Principle 2: Operable

### 2.1 Keyboard Accessible
- [ ] All interactive elements are reachable via Tab key
- [ ] No keyboard traps (can always Tab away from any element)
- [ ] Custom widgets support expected keyboard patterns
- [ ] Skip-to-main-content link is provided

### 2.4 Navigable
- [ ] Page has a descriptive `<title>`
- [ ] Focus order follows logical reading sequence
- [ ] Focus is visible on all interactive elements
- [ ] Link text is descriptive (no "click here" or "read more" alone)
- [ ] Multiple navigation mechanisms (menu, search, sitemap)

### 2.5 Input Modalities
- [ ] Multi-pointer gestures have single-pointer alternatives
- [ ] Pointer cancellation (up-event triggers action, not down-event)
- [ ] Touch targets are at least 44x44 CSS pixels
- [ ] Motion-triggered actions can be disabled or have alternatives

## Principle 3: Understandable

### 3.1 Readable
- [ ] Page language is declared (`<html lang="...">`)
- [ ] Language changes are marked (`<span lang="...">`)

### 3.2 Predictable
- [ ] No unexpected context change on focus
- [ ] No unexpected context change on input
- [ ] Navigation is consistent across pages
- [ ] Components with same function have same label

### 3.3 Input Assistance
- [ ] Form errors are identified in text (not color alone)
- [ ] Error messages describe how to fix the problem
- [ ] Required fields are clearly marked
- [ ] Input hints/examples are provided for complex fields

## Principle 4: Robust

### 4.1 Compatible
- [ ] HTML validates (no duplicate IDs, proper nesting)
- [ ] ARIA roles, states, and properties are valid
- [ ] Custom components have appropriate ARIA patterns
- [ ] Status messages use `role="alert"` or `aria-live`

## Quick Testing Checklist

```bash
# Automated tools to run
npx axe-cli https://example.com
npx lighthouse https://example.com --only-categories=accessibility
npx pa11y https://example.com
```

## Severity Levels

| Severity | Description | WCAG Level |
|----------|-------------|------------|
| Critical | Blocks access entirely | A |
| Major | Significant barrier | A/AA |
| Minor | Inconvenience | AA |
| Best Practice | Not required but recommended | AAA |
