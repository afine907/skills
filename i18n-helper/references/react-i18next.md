# React i18next Reference

## Setup

### Installation

```bash
npm install react-i18next i18next i18next-browser-languagedetector
```

### Configuration

```typescript
// i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import en from './locales/en.json';
import zh from './locales/zh.json';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      zh: { translation: zh },
    },
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already escapes
    },
  });

export default i18n;
```

### Entry Point

```tsx
// main.tsx
import './i18n';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

## Translation Files

### Structure (en.json)

```json
{
  "common": {
    "loading": "Loading...",
    "error": "Something went wrong",
    "save": "Save",
    "cancel": "Cancel"
  },
  "nav": {
    "home": "Home",
    "about": "About",
    "contact": "Contact Us"
  },
  "user": {
    "greeting": "Hello, {{name}}!",
    "profile": "{{name}}'s Profile",
    "memberSince": "Member since {{date, datetime}}",
    "itemCount": "{{count}} item",
    "itemCount_other": "{{count}} items"
  }
}
```

## Usage in Components

### Basic Translation

```tsx
import { useTranslation } from 'react-i18next';

function Header() {
  const { t } = useTranslation();

  return (
    <nav>
      <a href="/">{t('nav.home')}</a>
      <a href="/about">{t('nav.about')}</a>
    </nav>
  );
}
```

### Interpolation

```tsx
function UserProfile({ user }) {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{t('user.greeting', { name: user.name })}</h1>
      <p>{t('user.itemCount', { count: user.items.length })}</p>
    </div>
  );
}
```

### Plurals

```json
{
  "cart": {
    "item": "{{count}} item in your cart",
    "item_other": "{{count}} items in your cart"
  }
}
```

```tsx
function CartSummary({ count }) {
  const { t } = useTranslation();
  return <span>{t('cart.item', { count })}</span>;
}
```

### Formatting

```tsx
function OrderDetails({ order }) {
  const { t } = useTranslation();

  return (
    <div>
      {/* Date formatting */}
      <p>{t('order.date', { date: order.createdAt, formatParams: {
        date: { year: 'numeric', month: 'long', day: 'numeric' }
      }})}</p>

      {/* Number formatting */}
      <p>{t('order.total', { total: order.total, formatParams: {
        total: { style: 'currency', currency: 'USD' }
      }})}</p>
    </div>
  );
}
```

### Namespace Separation

```tsx
// Use specific namespace
function AdminPanel() {
  const { t } = useTranslation('admin');
  return <h1>{t('dashboard.title')}</h1>;
}

// Use multiple namespaces
function Page() {
  const { t } = useTranslation(['common', 'page']);
  return (
    <div>
      <h1>{t('page:title')}</h1>
      <button>{t('common:save')}</button>
    </div>
  );
}
```

### Trans Component (Rich Text)

```tsx
import { Trans } from 'react-i18next';

function Welcome({ name }) {
  const { t } = useTranslation();

  return (
    <Trans i18nKey="welcome" values={{ name }}>
      Hello, <strong>{{ name }}</strong>! Welcome to our app.
    </Trans>
  );
}
```

```json
{
  "welcome": "Hello, <1>{{name}}</1>! Welcome to our app."
}
```

## Language Switcher

```tsx
function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    document.documentElement.lang = lng;
  };

  return (
    <select
      value={i18n.language}
      onChange={(e) => changeLanguage(e.target.value)}
    >
      <option value="en">English</option>
      <option value="zh">Chinese</option>
      <option value="ja">Japanese</option>
    </select>
  );
}
```

## Lazy Loading Translations

```typescript
// i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
  });
```

## Testing

```tsx
import { render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from './test-i18n';

function renderWithI18n(component: React.ReactNode) {
  return render(
    <I18nextProvider i18n={i18n}>
      {component}
    </I18nextProvider>
  );
}

test('renders greeting', () => {
  renderWithI18n(<UserProfile user={{ name: 'Alice' }} />);
  expect(screen.getByText(/Hello, Alice/)).toBeInTheDocument();
});
```

## TypeScript Support

```typescript
// i18next.d.ts
import 'react-i18next';
import en from './locales/en.json';

declare module 'react-i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation';
    resources: {
      translation: typeof en;
    };
  }
}
```

This gives you type-safe keys: `t('user.greeting')` autocompletes and type-checks interpolation params.
