---
name: mobile-service-creator
description: |
  【移动端脚手架】快速创建 React Native / Flutter 移动应用项目。
  
  触发时机：
  - 用户要求"创建移动应用"、"React Native项目"、"Flutter项目"
  - 需要搭建移动端项目结构
  
  生成完整项目结构和示例代码。
category: development
---

# Mobile Service Creator — 移动端项目脚手架

快速创建 React Native / Flutter 移动应用项目。

## Goal

快速搭建高质量的移动应用项目脚手架，支持 React Native 和 Flutter 两大主流框架。提供完整的项目结构、导航配置、状态管理、API 集成和测试设置。

## Trigger

- 用户要求"创建移动应用"、"React Native项目"、"Flutter项目"
  - 需要搭建移动端项目结构
  - 初始化移动端项目结构和配置

## 框架选择指南

### React Native 适用场景

| 场景 | 原因 |
|------|------|
| 团队熟悉 JavaScript/TypeScript | 学习成本低，复用前端技能 |
| 需要 Web 共享代码 | 可与 React Web 共享业务逻辑 |
| 已有 React 生态依赖 | npm 生态丰富 |
| 需要热更新 | CodePush 等方案成熟 |
| 原生模块需求较少 | 纯 JS 方案足够 |

### Flutter 适用场景

| 场景 | 原因 |
|------|------|
| 追求高性能 UI | 自绘引擎，性能接近原生 |
| 需要高度自定义 UI | Widget 系统灵活 |
| 团队熟悉 Dart 或愿意学习 | Dart 语言现代化 |
| 需要跨平台一致性 | iOS/Android 表现一致 |
| 复杂动画需求 | 动画系统强大 |

### 决策流程

```
开始
  │
  ├─ 团队有 JS/TS 经验？──是──→ React Native
  │
  ├─ 需要极致性能？──是──→ Flutter
  │
  ├─ 需要 Web 代码复用？──是──→ React Native
  │
  ├─ UI 高度自定义？──是──→ Flutter
  │
  └─ 默认 → React Native（生态更成熟）
```

## 工作流程

### 步骤 1：确认框架和技术栈

询问用户：
1. 目标框架（React Native / Flutter）
2. 开发语言偏好（TypeScript / JavaScript / Dart）
3. 状态管理方案
4. 是否需要原生模块

### 步骤 2：初始化项目

#### React Native 项目初始化

```bash
# 使用 React Native CLI
npx react-native init MyProject --template react-native-template-typescript

# 或使用 Expo（推荐新手）
npx create-expo-app MyProject --template blank-typescript
```

#### Flutter 项目初始化

```bash
flutter create --org com.example my_project
cd my_project
```

### 步骤 3：生成项目结构

根据选择的框架生成标准化目录结构（详见 `references/react-native-patterns.md` 和 `references/flutter-patterns.md`）。

### 步骤 4：配置核心模块

- 导航系统
- 状态管理
- 网络请求
- 主题系统
- 国际化（可选）

### 步骤 5：生成示例代码

为每个核心模块生成示例代码，展示最佳实践。

## React Native 项目结构

```
my-rn-app/
├── src/
│   ├── app/
│   │   ├── App.tsx              # 应用入口
│   │   ├── navigation/
│   │   │   ├── index.tsx        # 导航配置
│   │   │   ├── MainStack.tsx    # 主导航栈
│   │   │   └── AuthStack.tsx    # 认证导航栈
│   │   └── providers/
│   │       ├── ThemeProvider.tsx
│   │       └── AuthProvider.tsx
│   ├── screens/
│   │   ├── Home/
│   │   │   ├── HomeScreen.tsx
│   │   │   ├── HomeScreen.styles.ts
│   │   │   └── HomeScreen.test.tsx
│   │   ├── Profile/
│   │   └── Settings/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   └── Card/
│   │   └── layout/
│   │       ├── Header/
│   │       └── TabBar/
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.ts        # Axios/ fetch 配置
│   │   │   ├── auth.ts
│   │   │   └── user.ts
│   │   └── storage/
│   │       └── asyncStorage.ts
│   ├── store/
│   │   ├── index.ts             # 状态管理入口
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   └── userSlice.ts
│   │   └── hooks/
│   │       ├── useAuth.ts
│   │       └── useUser.ts
│   ├── hooks/
│   │   ├── useApi.ts
│   │   └── useForm.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── helpers.ts
│   │   └── validators.ts
│   ├── theme/
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   └── spacing.ts
│   └── types/
│       ├── api.ts
│       └── navigation.ts
├── android/
├── ios/
├── __tests__/
├── .eslintrc.js
├── .prettierrc
├── tsconfig.json
├── jest.config.js
└── package.json
```

## Flutter 项目结构

```
my_flutter_app/
├── lib/
│   ├── main.dart                # 应用入口
│   ├── app/
│   │   ├── app.dart             # MaterialApp 配置
│   │   ├── routes/
│   │   │   ├── app_router.dart
│   │   │   └── route_names.dart
│   │   └── themes/
│   │       ├── app_theme.dart
│   │       └── app_colors.dart
│   ├── features/
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   │   ├── repositories/
│   │   │   │   └── datasources/
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   ├── repositories/
│   │   │   │   └── usecases/
│   │   │   └── presentation/
│   │   │       ├── screens/
│   │   │       ├── widgets/
│   │   │       └── providers/
│   │   ├── home/
│   │   └── profile/
│   ├── core/
│   │   ├── network/
│   │   │   ├── api_client.dart
│   │   │   ├── api_endpoints.dart
│   │   │   └── interceptors.dart
│   │   ├── storage/
│   │   │   └── local_storage.dart
│   │   ├── error/
│   │   │   ├── exceptions.dart
│   │   │   └── failures.dart
│   │   └── utils/
│   │       ├── constants.dart
│   │       └── extensions.dart
│   ├── shared/
│   │   ├── widgets/
│   │   │   ├── app_button.dart
│   │   │   ├── app_input.dart
│   │   │   └── app_card.dart
│   │   └── mixins/
│   │       └── validation_mixin.dart
│   └── config/
│       ├── env.dart
│       └── dependencies.dart
├── test/
│   ├── unit/
│   ├── widget/
│   └── integration/
├── pubspec.yaml
├── analysis_options.yaml
└── README.md
```

## 导航模式

### React Navigation 配置

```typescript
// src/app/navigation/index.tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

export default function AppNavigation() {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Main" component={MainTabs} />
        <Stack.Screen name="Detail" component={DetailScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### Flutter Navigator 2.0 配置

```dart
// lib/app/routes/app_router.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

final goRouter = GoRouter(
  initialLocation: '/',
  routes: [
    StatefulShellRoute.indexedStack(
      builder: (context, state, navigationShell) {
        return MainScaffold(navigationShell: navigationShell);
      },
      branches: [
        StatefulShellBranch(routes: [
          GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
        ]),
        StatefulShellBranch(routes: [
          GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
        ]),
        StatefulShellBranch(routes: [
          GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
        ]),
      ],
    ),
    GoRoute(
      path: '/detail/:id',
      builder: (context, state) => DetailScreen(id: state.pathParameters['id']!),
    ),
  ],
);
```

## 状态管理

### Zustand (React Native)

```typescript
// src/store/useAuthStore.ts
import { create } from 'zustand';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,
  login: async (credentials) => {
    set({ isLoading: true });
    try {
      const { user, token } = await authApi.login(credentials);
      set({ user, token, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
  logout: () => set({ user: null, token: null }),
}));
```

### Riverpod (Flutter)

```dart
// lib/features/auth/presentation/providers/auth_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(authRepositoryProvider));
});

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _repository;

  AuthNotifier(this._repository) : super(AuthState.initial());

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true);
    try {
      final result = await _repository.login(email, password);
      state = state.copyWith(user: result.user, token: result.token, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void logout() {
    state = AuthState.initial();
  }
}
```

## API 集成

### React Native API 客户端

```typescript
// src/services/api/client.ts
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const apiClient = axios.create({
  baseURL: process.env.API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // 处理 token 过期
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Flutter API 客户端

```dart
// lib/core/network/api_client.dart
import 'package:dio/dio.dart';

class ApiClient {
  late final Dio _dio;

  ApiClient({required String baseUrl}) {
    _dio = Dio(BaseOptions(baseUrl: baseUrl, connectTimeout: const Duration(seconds: 10)));
    _dio.interceptors.addAll([
      AuthInterceptor(),
      LogInterceptor(requestBody: true, responseBody: true),
    ]);
  }

  Future<Response> get(String path, {Map<String, dynamic>? params}) {
    return _dio.get(path, queryParameters: params);
  }

  Future<Response> post(String path, {dynamic data}) {
    return _dio.post(path, data: data);
  }
}
```

## 平台特定代码

### React Native 平台判断

```typescript
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.OS === 'ios' ? 44 : 0,
    ...Platform.select({
      ios: { shadowColor: '#000', shadowOffset: { width: 0, height: 2 } },
      android: { elevation: 4 },
    }),
  },
});
```

### Flutter 平台判断

```dart
import 'dart:io';

Widget buildPlatformWidget() {
  if (Platform.isIOS) {
    return CupertinoButton(child: Text('iOS'), onPressed: () {});
  } else {
    return ElevatedButton(child: Text('Android'), onPressed: () {});
  }
}
```

## 测试设置

### React Native 测试

```typescript
// __tests__/HomeScreen.test.tsx
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import HomeScreen from '../src/screens/Home/HomeScreen';

describe('HomeScreen', () => {
  it('renders loading state initially', () => {
    const { getByTestId } = render(<HomeScreen />);
    expect(getByTestId('loading-indicator')).toBeTruthy();
  });

  it('displays data after loading', async () => {
    const { getByText } = render(<HomeScreen />);
    await waitFor(() => {
      expect(getByText('Welcome')).toBeTruthy();
    });
  });
});
```

### Flutter 测试

```dart
// test/widget/home_screen_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('HomeScreen displays welcome message', (tester) async {
    await tester.pumpWidget(
      ProviderScope(child: MaterialApp(home: HomeScreen())),
    );
    expect(find.text('Welcome'), findsOneWidget);
  });
}
```

## 最佳实践

1. **TypeScript 优先**：React Native 项目始终使用 TypeScript
2. **Clean Architecture**：Flutter 项目采用分层架构（data/domain/presentation）
3. **组件化**：提取可复用的 UI 组件
4. **类型安全**：定义完整的类型/模型
5. **错误处理**：统一的错误处理机制
6. **性能优化**：使用 `React.memo`/`const` Widget 减少不必要的重建
7. **测试覆盖**：核心业务逻辑必须有单元测试

## 输出模板

Claude 创建移动应用时，按以下格式输出：

```
## 移动应用脚手架报告

### 框架选择
- 框架：{React Native / Flutter}
- 理由：{选择原因}

### 生成文件清单
| 文件路径 | 说明 | 状态 |
|---------|------|------|
| src/app/App.tsx / lib/main.dart | 应用入口 | 新建 |
| src/app/navigation/ / lib/app/routes/ | 导航配置 | 新建 |
| src/store/ / lib/features/ | 状态管理 | 新建 |
| src/services/api/ / lib/core/network/ | API 客户端 | 新建 |
| src/theme/ / lib/app/themes/ | 主题配置 | 新建 |
| ... | ... | ... |

### 关键代码
（展示导航配置、状态管理、API 客户端的完整代码）

### 后续步骤
1. cd {project-name} && npm install / flutter pub get
2. 配置开发环境（Xcode / Android Studio）
3. 运行 npm start / flutter run 启动
```

**端到端示例：**

用户输入：`创建一个 Flutter 电商 App`

Claude 输出以上模板，文件清单中包含 Flutter Clean Architecture 目录结构（core/features/shared）、GoRouter 导航、Riverpod 状态管理、Dio API 客户端等，并附上关键代码片段。

## 快速使用

```
# 创建 React Native 项目
创建一个 React Native 项目，用于社交聊天应用，使用 Expo

# 创建 Flutter 项目
创建一个 Flutter 电商 App，使用 Riverpod + GoRouter

# 添加功能模块
为项目添加用户登录模块，包含注册、登录、找回密码

# 生成导航
为项目添加底部 Tab 导航和 Stack 导航
```

## 不适用

- Web 前端项目 → 使用 [react-service-creator](../react-service-creator/SKILL.md) 或 [vue-service-creator](../vue-service-creator/SKILL.md)
- 后端 API 服务 → 使用 [typescript-service-creator](../typescript-service-creator/SKILL.md) 或 [python-service-creator](../python-service-creator/SKILL.md)
- 桌面应用 → 使用 Electron / Tauri 方案

## 边界情况

- **原生模块集成**：当需要使用原生功能时，生成对应的原生代码桥接
- **多环境配置**：支持 dev/staging/prod 环境切换
- **深链接处理**：配置 Deep Link 和 Universal Link
- **推送通知**：集成 FCM/APNs 推送服务
- **离线支持**：配置离线数据缓存策略

## 参考资料

- React Native 模式: [references/react-native-patterns.md](references/react-native-patterns.md)
- Flutter 模式: [references/flutter-patterns.md](references/flutter-patterns.md)
