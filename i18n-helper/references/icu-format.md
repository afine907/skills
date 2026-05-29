# ICU Message Format Reference

## Overview

ICU (International Components for Unicode) MessageFormat is the industry standard for locale-aware message formatting. Used by Java, ICU4J, FormatJS (React), and many translation platforms.

## Basic Syntax

### Simple Replacement

```
Hello, {name}!
```

### With Formatting

```
The total is {amount, number, ::currency/USD}.
The date is {date, date, long}.
The time is {time, time, short}.
```

## Plural Rules

### Basic Plural

```
{count, plural,
  =0 {No items}
  one {# item}
  other {# items}
}
```

### With Explicit Values

```
{count, plural,
  =0 {You have no messages}
  =1 {You have one message}
  =2 {You have a couple of messages}
  few {You have # messages}
  many {You have # messages}
  other {You have # messages}
}
```

### Plural Categories by Language

| Language | Categories |
|----------|-----------|
| English | one, other |
| Chinese | other |
| Arabic | zero, one, two, few, many, other |
| Russian | one, few, many, other |
| Polish | one, few, many, other |
| Japanese | other |
| German | one, other |
| French | one, many, other |

## Gender/Select

```
{gender, select,
  male {He updated his profile}
  female {She updated her profile}
  other {They updated their profile}
}
```

### Combined Select + Plural

```
{gender, select,
  male {He has {count, plural,
    =0 {no items}
    one {# item}
    other {# items}
  }}
  female {She has {count, plural,
    =0 {no items}
    one {# item}
    other {# items}
  }}
  other {They have {count, plural,
    =0 {no items}
    one {# item}
    other {# items}
  }}
}
```

## Number Formatting

### Basic

```
{amount, number}
```

### Currency

```
{amount, number, ::currency/USD}     → $1,234.56
{amount, number, ::currency/EUR}     → €1,234.56
{amount, number, ::currency/CNY}     → ¥1,234.56
```

### Percent

```
{rate, number, ::percent}            → 45%
{rate, number, ::percent/precision-integer} → 45%
```

### Integer

```
{count, number, ::integer}           → 1,234
```

### Custom Scales

```
{bytes, number, ::bytes/iec-kib}     → 1.5 KiB
{bytes, number, ::bytes/metric-kb}   → 1.5 KB
```

## Date and Time Formatting

### Date Styles

```
{date, date, short}    → 1/15/24
{date, date, medium}   → Jan 15, 2024
{date, date, long}     → January 15, 2024
{date, date, full}     → Monday, January 15, 2024
```

### Time Styles

```
{time, time, short}    → 2:30 PM
{time, time, medium}   → 2:30:00 PM
{time, time, long}     → 2:30:00 PM EST
{time, time, full}     → 2:30:00 PM Eastern Standard Time
```

### Custom Skeletons

```
{date, date, ::yMMMd}           → Jan 15, 2024
{date, date, ::yMMMMd}          → January 15, 2024
{date, date, ::yMMMdHmm}        → Jan 15, 2024, 14:30
{date, date, ::EEEEdMMMM}       → Monday, January 15
```

## Relative Time (FormatJS Extension)

```
You joined {date, relativeTime}
You joined {date, relativeTime, short}
```

## Selectordinal (Ordinal Plurals)

```
{position, selectordinal,
  one {#st place}
  two {#nd place}
  few {#rd place}
  other {#th place}
}

// Results:
// 1 → "1st place"
// 2 → "2nd place"
// 3 → "3rd place"
// 11 → "11th place"
// 22 → "22nd place"
```

## Nested Messages

```
{count, plural,
  =0 {No results}
  other {
    {count, plural,
      =1 {One result found}
      other {# results found}
    }
    {hasMore, select,
      yes {, showing first {visible}}
      other {}
    }
  }
}
```

## React Integration (FormatJS)

```tsx
import { IntlProvider, FormattedMessage, FormattedNumber, FormattedDate } from 'react-intl';

function App() {
  return (
    <IntlProvider locale="en" messages={messages}>
      <FormattedMessage
        id="user.greeting"
        defaultMessage="Hello, {name}!"
        values={{ name: 'Alice' }}
      />

      <FormattedNumber value={1234.56} style="currency" currency="USD" />

      <FormattedDate value={new Date()} year="numeric" month="long" day="numeric" />
    </IntlProvider>
  );
}
```

## Translation Platform Compatibility

| Platform | ICU Support | Notes |
|----------|-------------|-------|
| Crowdin | Full | Auto-validates ICU syntax |
| Lokalise | Full | Visual editor for plurals |
| Transifex | Full | Good plural handling |
| POEditor | Partial | Basic interpolation only |
| Weblate | Full | Built-in ICU validation |

## Best Practices

1. **Never concatenate translated strings** - Use full sentences with placeholders
2. **Always provide `other`** - It is the required fallback
3. **Use `#` for the variable in plurals** - It is replaced by the formatted number
4. **Keep messages atomic** - One message per UI element
5. **Use named placeholders** - `{name}` not `{0}` for readability
6. **Add comments for translators** - Explain context, character limits

## Common Mistakes

```
// BAD: Concatenating translated fragments
t('prefix') + ' ' + t('suffix')

// GOOD: Full message with placeholders
t('fullMessage', { prefix, suffix })

// BAD: Assuming English plural rules
{count, plural, =0 {none} =1 {one} other {many}}

// GOOD: Proper plural categories
{count, plural, =0 {none} one {# item} other {# items}}
```
