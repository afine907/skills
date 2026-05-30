# React Component Patterns

## Composition Patterns

### Container/Presentational

Separate data fetching (container) from rendering (presentational).

```tsx
// Presentational: pure rendering, receives props
function UserCard({ name, email, avatar }: UserCardProps) {
  return (
    <div className="user-card">
      <img src={avatar} alt={name} />
      <h3>{name}</h3>
      <p>{email}</p>
    </div>
  );
}

// Container: handles data fetching and logic
function UserCardContainer({ userId }: { userId: string }) {
  const { data, loading, error } = useQuery(GET_USER, { variables: { id: userId } });

  if (loading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;

  return <UserCard name={data.user.name} email={data.user.email} avatar={data.user.avatar} />;
}
```

### Render Props

Share behavior via a function that returns elements.

```tsx
interface MouseTrackerProps {
  children: (position: { x: number; y: number }) => React.ReactNode;
}

function MouseTracker({ children }: MouseTrackerProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    setPosition({ x: e.clientX, y: e.clientY });
  };

  return <div onMouseMove={handleMouseMove}>{children(position)}</div>;
}

// Usage
<MouseTracker>
  {({ x, y }) => (
    <div>
      Mouse is at ({x}, {y})
    </div>
  )}
</MouseTracker>
```

### Compound Components

Related components that work together with shared state.

```tsx
function Tabs({ children, defaultTab }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

function TabList({ children }: { children: React.ReactNode }) {
  return <div className="tab-list" role="tablist">{children}</div>;
}

function Tab({ value, children }: { value: string; children: React.ReactNode }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  return (
    <button
      role="tab"
      aria-selected={activeTab === value}
      onClick={() => setActiveTab(value)}
    >
      {children}
    </button>
  );
}

function TabPanel({ value, children }: { value: string; children: React.ReactNode }) {
  const { activeTab } = useContext(TabsContext);
  if (activeTab !== value) return null;
  return <div role="tabpanel">{children}</div>;
}

// Usage
<Tabs defaultTab="profile">
  <TabList>
    <Tab value="profile">Profile</Tab>
    <Tab value="settings">Settings</Tab>
  </TabList>
  <TabPanel value="profile">Profile content</TabPanel>
  <TabPanel value="settings">Settings content</TabPanel>
</Tabs>
```

## Hook Patterns

### Custom Hook for API Calls

```tsx
function useApi<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchData() {
      try {
        setLoading(true);
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error(response.statusText);
        setData(await response.json());
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          setError(err);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    return () => controller.abort();
  }, [url]);

  return { data, loading, error, refetch: () => {/* ... */} };
}
```

### useLocalStorage

```tsx
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}
```

### useDebounce

```tsx
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Usage
function SearchInput() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery) {
      searchAPI(debouncedQuery);
    }
  }, [debouncedQuery]);

  return <input value={query} onChange={(e) => setQuery(e.target.value)} />;
}
```

## Higher-Order Components (HOC)

```tsx
function withAuth<P extends object>(Component: React.ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { user, loading } = useAuth();

    if (loading) return <Spinner />;
    if (!user) return <Navigate to="/login" />;

    return <Component {...props} />;
  };
}

// Usage
const ProtectedDashboard = withAuth(Dashboard);
```

## Prop Patterns

### Discriminated Unions

```tsx
type ButtonProps =
  | { variant: 'primary'; onClick: () => void; children: React.ReactNode }
  | { variant: 'link'; href: string; children: React.ReactNode }
  | { variant: 'icon'; icon: IconType; 'aria-label': string };

function Button(props: ButtonProps) {
  switch (props.variant) {
    case 'primary':
      return <button onClick={props.onClick}>{props.children}</button>;
    case 'link':
      return <a href={props.href}>{props.children}</a>;
    case 'icon':
      return <button aria-label={props['aria-label']}><props.icon /></button>;
  }
}
```

### Slot Pattern

```tsx
interface CardProps {
  header?: React.ReactNode;
  footer?: React.ReactNode;
  children: React.ReactNode;
}

function Card({ header, footer, children }: CardProps) {
  return (
    <div className="card">
      {header && <div className="card-header">{header}</div>}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}

// Usage
<Card
  header={<h2>Title</h2>}
  footer={<Button>Save</Button>}
>
  <p>Content goes here</p>
</Card>
```

## Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| Prop drilling (deep) | Passing props through many levels | Context, composition, or state management |
| God component | One component doing everything | Split into smaller components |
| Inline objects/functions | Creates new references every render | useMemo, useCallback, move outside |
| useEffect for derived state | Synchronous derived values as effects | Compute directly in render |
| useState for URL state | Duplicates URL state in component | Use URL params (react-router) |
| Mutating state | Modifying state objects directly | Create new objects/arrays |
