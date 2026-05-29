# React State Management Reference

## Decision Guide

```
What kind of state?
├── UI-only (modal open, dropdown selected) → useState / useReducer
├── Shared between nearby components → Lifting state + props
├── Shared across distant components → Context or Zustand
├── Server data (API responses) → TanStack Query / SWR
├── Complex form state → React Hook Form / Formik
├── URL state (filters, pagination) → URL params (react-router)
└── Global client state (auth, theme) → Zustand / Jotai
```

## useState

Best for: Simple, independent state values.

```tsx
const [count, setCount] = useState(0);
const [isOpen, setIsOpen] = useState(false);
const [user, setUser] = useState<User | null>(null);
```

## useReducer

Best for: Complex state with multiple related updates.

```tsx
type State = { items: Item[]; loading: boolean; error: string | null };
type Action =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; items: Item[] }
  | { type: 'FETCH_ERROR'; error: string }
  | { type: 'ADD_ITEM'; item: Item }
  | { type: 'REMOVE_ITEM'; id: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, items: action.items };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.error };
    case 'ADD_ITEM':
      return { ...state, items: [...state.items, action.item] };
    case 'REMOVE_ITEM':
      return { ...state, items: state.items.filter(i => i.id !== action.id) };
  }
}

function ItemList() {
  const [state, dispatch] = useReducer(reducer, {
    items: [], loading: false, error: null,
  });
  // ...
}
```

## Context

Best for: Infrequently changing global state (theme, locale, auth).

```tsx
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const login = async (credentials: Credentials) => {
    const user = await authAPI.login(credentials);
    setUser(user);
  };

  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
```

**Caution**: Context re-renders all consumers when value changes. Split contexts for frequently changing values.

## Zustand

Best for: Simple, lightweight global state without boilerplate.

```typescript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
  total: () => number;
}

const useCartStore = create<CartStore>()(
  devtools(
    persist(
      (set, get) => ({
        items: [],
        addItem: (item) =>
          set((state) => ({ items: [...state.items, item] })),
        removeItem: (id) =>
          set((state) => ({ items: state.items.filter(i => i.id !== id) })),
        clearCart: () => set({ items: [] }),
        total: () =>
          get().items.reduce((sum, item) => sum + item.price * item.quantity, 0),
      }),
      { name: 'cart-storage' }
    )
  )
);

// Usage in component
function Cart() {
  const items = useCartStore((s) => s.items);
  const removeItem = useCartStore((s) => s.removeItem);
  const total = useCartStore((s) => s.total());
  // ...
}
```

## TanStack Query (React Query)

Best for: Server state - API data fetching, caching, synchronization.

```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Query
function Users() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json()),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <UserList users={data} />;
}

// Mutation
function CreateUser() {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (newUser: CreateUserInput) =>
      fetch('/api/users', { method: 'POST', body: JSON.stringify(newUser) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      mutation.mutate({ name, email });
    }}>
      {/* form fields */}
      <button disabled={mutation.isPending}>Create</button>
    </form>
  );
}
```

## Jotai

Best for: Atomic state, fine-grained reactivity.

```typescript
import { atom, useAtom, useAtomValue } from 'jotai';

const countAtom = atom(0);
const doubledAtom = atom((get) => get(countAtom) * 2);
const asyncAtom = atom(async (get) => {
  const count = get(countAtom);
  const response = await fetch(`/api/data?page=${count}`);
  return response.json();
});

function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const doubled = useAtomValue(doubledAtom);
  return (
    <div>
      <p>{count} x 2 = {doubled}</p>
      <button onClick={() => setCount(c => c + 1)}>+1</button>
    </div>
  );
}
```

## State Management Comparison

| Solution | Boilerplate | DevTools | Bundle Size | Best For |
|----------|-------------|----------|-------------|----------|
| useState/useReducer | None | React DevTools | 0 KB | Simple local state |
| Context | Low | React DevTools | 0 KB | Infrequent updates |
| Zustand | Very low | Yes | ~1 KB | Simple global state |
| Jotai | Low | Yes | ~2 KB | Atomic state |
| Redux Toolkit | Medium | Excellent | ~11 KB | Complex apps, large teams |
| TanStack Query | Low | Yes | ~13 KB | Server state |
| MobX | Low | Yes | ~16 KB | Complex reactive state |

## Patterns to Avoid

| Pattern | Problem | Solution |
|---------|---------|----------|
| Global state for everything | Unnecessary re-renders, hard to reason about | Use local state by default |
| Prop drilling 5+ levels | Hard to maintain, refactor | Context or state library |
| useEffect to sync state | Race conditions, stale closures | Derive during render |
| Duplicated state | Sync bugs between sources | Single source of truth |
| Mutating state objects | Components don't re-render | Always create new references |
