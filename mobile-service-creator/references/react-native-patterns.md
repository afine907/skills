# React Native Patterns Reference

## 项目初始化配置

### TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "commonjs",
    "lib": ["es2020"],
    "jsx": "react-native",
    "strict": true,
    "moduleResolution": "node",
    "baseUrl": ".",
    "paths": {
      "@components/*": ["src/components/*"],
      "@screens/*": ["src/screens/*"],
      "@services/*": ["src/services/*"],
      "@store/*": ["src/store/*"],
      "@hooks/*": ["src/hooks/*"],
      "@utils/*": ["src/utils/*"],
      "@theme/*": ["src/theme/*"]
    },
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

### ESLint 配置

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  extends: [
    '@react-native',
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  plugins: ['@typescript-eslint', 'react-hooks'],
  rules: {
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  },
};
```

## 常用组件模式

### 自定义 Button 组件

```typescript
// src/components/common/Button/Button.tsx
import React from 'react';
import { TouchableOpacity, Text, ActivityIndicator, StyleSheet, ViewStyle } from 'react-native';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline';
  loading?: boolean;
  disabled?: boolean;
  style?: ViewStyle;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  loading = false,
  disabled = false,
  style,
}) => {
  const buttonStyle = [styles.base, styles[variant], disabled && styles.disabled, style];

  return (
    <TouchableOpacity style={buttonStyle} onPress={onPress} disabled={disabled || loading}>
      {loading ? (
        <ActivityIndicator color="#fff" />
      ) : (
        <Text style={[styles.text, styles[`${variant}Text`]]}>{title}</Text>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: { paddingVertical: 12, paddingHorizontal: 24, borderRadius: 8, alignItems: 'center' },
  primary: { backgroundColor: '#007AFF' },
  secondary: { backgroundColor: '#6C757D' },
  outline: { backgroundColor: 'transparent', borderWidth: 1, borderColor: '#007AFF' },
  disabled: { opacity: 0.5 },
  text: { fontSize: 16, fontWeight: '600' },
  primaryText: { color: '#fff' },
  secondaryText: { color: '#fff' },
  outlineText: { color: '#007AFF' },
});
```

### 自定义 Hook 模式

```typescript
// src/hooks/useApi.ts
import { useState, useCallback } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>(apiFunction: (...args: any[]) => Promise<T>) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: any[]) => {
      setState({ data: null, loading: true, error: null });
      try {
        const data = await apiFunction(...args);
        setState({ data, loading: false, error: null });
        return data;
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        setState({ data: null, loading: false, error: message });
        throw error;
      }
    },
    [apiFunction]
  );

  return { ...state, execute };
}
```

## 状态管理模式

### Redux Toolkit 配置

```typescript
// src/store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { authSlice } from './slices/authSlice';
import { userSlice } from './slices/userSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
    user: userSlice.reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Zustand 中间件模式

```typescript
// src/store/middleware/logger.ts
import { StateCreator, StoreMutatorIdentifier } from 'zustand';

type Logger = <T extends unknown>(
  f: StateCreator<T, [], []>,
  name?: string
) => StateCreator<T, [], []>;

export const logger: Logger = (f, name) => (set, get, store) => {
  const loggedSet: typeof set = (...args) => {
    const before = get();
    set(...args);
    const after = get();
    console.log(`[${name || 'store'}]`, { before, after });
  };
  return f(loggedSet, get, store);
};
```

## 导航高级模式

### 类型安全的导航

```typescript
// src/types/navigation.ts
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import { CompositeScreenProps, NavigatorScreenParams } from '@react-navigation/native';

export type MainTabParamList = {
  Home: undefined;
  Profile: undefined;
  Settings: undefined;
};

export type RootStackParamList = {
  Main: NavigatorScreenParams<MainTabParamList>;
  Detail: { id: string };
  EditProfile: { userId: string };
};

export type RootStackScreenProps<T extends keyof RootStackParamList> = NativeStackScreenProps<
  RootStackParamList,
  T
>;

export type MainTabScreenProps<T extends keyof MainTabParamList> = CompositeScreenProps<
  BottomTabScreenProps<MainTabParamList, T>,
  NativeStackScreenProps<RootStackParamList>
>;
```

## 性能优化模式

### 列表优化

```typescript
import { FlashList } from '@shopify/flash-list';

interface Item { id: string; title: string; }

const OptimizedList: React.FC<{ items: Item[] }> = ({ items }) => {
  return (
    <FlashList
      data={items}
      renderItem={({ item }) => <ListItem title={item.title} />}
      estimatedItemSize={80}
      keyExtractor={(item) => item.id}
    />
  );
};
```

### 图片缓存

```typescript
import FastImage from 'react-native-fast-image';

const CachedImage: React.FC<{ uri: string }> = ({ uri }) => (
  <FastImage
    style={{ width: 100, height: 100 }}
    source={{ uri, priority: FastImage.priority.normal }}
    resizeMode={FastImage.resizeMode.cover}
  />
);
```

## 错误处理模式

### 全局错误边界

```typescript
// src/components/ErrorBoundary.tsx
import React, { Component, ErrorInfo } from 'react';
import { View, Text, Button } from 'react-native';

interface Props { children: React.ReactNode; }
interface State { hasError: boolean; error: Error | null; }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
    // 发送到错误追踪服务
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <Text>出错了</Text>
          <Button title="重试" onPress={() => this.setState({ hasError: false, error: null })} />
        </View>
      );
    }
    return this.props.children;
  }
}
```

## 常用依赖清单

```json
{
  "dependencies": {
    "@react-navigation/native": "^6.x",
    "@react-navigation/native-stack": "^6.x",
    "@react-navigation/bottom-tabs": "^6.x",
    "react-native-screens": "^3.x",
    "react-native-safe-area-context": "^4.x",
    "zustand": "^4.x",
    "axios": "^1.x",
    "@react-native-async-storage/async-storage": "^1.x",
    "react-native-fast-image": "^8.x",
    "@shopify/flash-list": "^1.x",
    "react-hook-form": "^7.x",
    "dayjs": "^1.x"
  },
  "devDependencies": {
    "@testing-library/react-native": "^12.x",
    "@types/react": "^18.x",
    "@typescript-eslint/eslint-plugin": "^6.x",
    "jest": "^29.x",
    "typescript": "^5.x"
  }
}
```
