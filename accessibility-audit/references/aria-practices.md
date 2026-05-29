# ARIA Best Practices

Guide to using WAI-ARIA roles, states, and properties correctly in web applications.

## First Rule of ARIA

Do not use ARIA if a native HTML element or attribute provides the semantics you need.

```html
<!-- Bad: Using ARIA for a button -->
<div role="button" tabindex="0" aria-pressed="false">Submit</div>

<!-- Good: Native button -->
<button type="submit">Submit</button>
```

## Landmark Roles

```html
<header role="banner">
  <nav role="navigation" aria-label="Main menu">...</nav>
</header>
<main role="main">
  <article role="article">
    <h1>Page Title</h1>
  </article>
  <aside role="complementary">...</aside>
</main>
<footer role="contentinfo">...</footer>
```

## Live Regions

Use `aria-live` to announce dynamic content changes to screen readers.

```html
<!-- Polite: waits for user to finish current task -->
<div aria-live="polite" aria-atomic="true">
  <span>3 results found</span>
</div>

<!-- Assertive: interrupts immediately (use sparingly) -->
<div role="alert">
  <span>Error: form submission failed</span>
</div>

<!-- Status: polite live region with role="status" -->
<div role="status" aria-live="polite">
  <span>Loading...</span>
</div>
```

## Common Widget Patterns

### Modal Dialog

```html
<div role="dialog" aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Action</h2>
  <p>Are you sure you want to delete this item?</p>
  <button aria-label="Cancel">Cancel</button>
  <button aria-label="Confirm delete">Delete</button>
</div>
```

### Tabs

```html
<div role="tablist" aria-label="Settings">
  <button role="tab" aria-selected="true" aria-controls="panel-1" id="tab-1">
    General
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-2" id="tab-2">
    Security
  </button>
</div>
<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  General settings content
</div>
<div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>
  Security settings content
</div>
```

### Accordion

```html
<h3>
  <button aria-expanded="false" aria-controls="sect-1">
    Section 1
  </button>
</h3>
<div id="sect-1" role="region" aria-labelledby="tab-1" hidden>
  Section content
</div>
```

### Combobox (Autocomplete)

```html
<div role="combobox" aria-expanded="false" aria-haspopup="listbox">
  <input type="text" aria-autocomplete="list" aria-controls="listbox-1">
</div>
<ul role="listbox" id="listbox-1">
  <li role="option" aria-selected="false">Option 1</li>
  <li role="option" aria-selected="true">Option 2</li>
</ul>
```

## States and Properties Reference

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `aria-expanded` | Toggle state for disclosure | `aria-expanded="true"` |
| `aria-hidden` | Hide from assistive tech | `aria-hidden="true"` |
| `aria-label` | Accessible name (no visible text) | `aria-label="Close"` |
| `aria-labelledby` | Points to labeling element | `aria-labelledby="id1"` |
| `aria-describedby` | Additional description | `aria-describedby="hint"` |
| `aria-required` | Marks required form fields | `aria-required="true"` |
| `aria-invalid` | Indicates validation error | `aria-invalid="true"` |
| `aria-disabled` | Disabled state for widgets | `aria-disabled="true"` |
| `aria-pressed` | Toggle button state | `aria-pressed="false"` |
| `aria-selected` | Selection in lists/tabs | `aria-selected="true"` |
| `aria-busy` | Loading or updating state | `aria-busy="true"` |
| `aria-current` | Current item in a set | `aria-current="page"` |

## Keyboard Interaction Patterns

| Widget | Key | Action |
|--------|-----|--------|
| Tabs | Arrow Left/Right | Move between tabs |
| Menu | Arrow Up/Down | Navigate items |
| Menu | Escape | Close menu |
| Dialog | Escape | Close dialog |
| Dialog | Tab | Trap focus within |
| Tree | Arrow Up/Down | Navigate nodes |
| Tree | Arrow Left | Collapse node |
| Tree | Arrow Right | Expand node |
| Combobox | Arrow Up/Down | Navigate options |
| Combobox | Enter | Select option |
| Combobox | Escape | Close listbox |

## Common Mistakes

1. **Using `role="button"` on `<div>`** -- use `<button>` instead
2. **Missing keyboard handler** -- ARIA role implies keyboard behavior
3. **Incorrect `aria-live`** -- `assertive` is disruptive; prefer `polite`
4. **Orphaned `aria-labelledby`** -- referenced ID must exist in DOM
5. **Using `aria-hidden="true"` on focusable elements** -- creates keyboard traps
6. **Missing `aria-expanded`** -- disclosure widgets must indicate state
