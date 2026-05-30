# Flutter Patterns Reference

## 项目配置

### pubspec.yaml 依赖

```yaml
name: my_flutter_app
description: A Flutter application
version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  # 状态管理
  flutter_riverpod: ^2.4.0
  riverpod_annotation: ^2.1.0
  # 导航
  go_router: ^12.0.0
  # 网络请求
  dio: ^5.3.0
  retrofit: ^4.0.0
  # 本地存储
  shared_preferences: ^2.2.0
  hive: ^2.2.0
  # UI 组件
  flutter_screenutil: ^5.9.0
  cached_network_image: ^3.3.0
  shimmer: ^3.0.0
  # 工具
  freezed_annotation: ^2.4.0
  json_annotation: ^4.8.0
  intl: ^0.18.0
  # 路径
  path_provider: ^2.1.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  # 代码生成
  build_runner: ^2.4.0
  freezed: ^2.4.0
  json_serializable: ^6.7.0
  riverpod_generator: ^2.3.0
  retrofit_generator: ^7.0.0
  # 测试
  mockito: ^5.4.0
  mocktail: ^1.0.0
  # Lint
  flutter_lints: ^3.0.0
  very_good_analysis: ^5.0.0
```

### analysis_options.yaml

```yaml
include: package:very_good_analysis/analysis_options.yaml

analyzer:
  exclude:
    - '**/*.g.dart'
    - '**/*.freezed.dart'
  errors:
    invalid_annotation_target: ignore

linter:
  rules:
    public_member_api_docs: false
    lines_longer_than_80_chars: false
```

## Clean Architecture 模式

### Feature 目录结构

```
features/
├── auth/
│   ├── data/
│   │   ├── datasources/
│   │   │   ├── auth_remote_datasource.dart
│   │   │   └── auth_local_datasource.dart
│   │   ├── models/
│   │   │   ├── user_model.dart
│   │   │   └── user_model.freezed.dart
│   │   └── repositories/
│   │       └── auth_repository_impl.dart
│   ├── domain/
│   │   ├── entities/
│   │   │   └── user.dart
│   │   ├── repositories/
│   │   │   └── auth_repository.dart
│   │   └── usecases/
│   │       ├── login_usecase.dart
│   │       └── logout_usecase.dart
│   └── presentation/
│       ├── providers/
│       │   ├── auth_provider.dart
│       │   └── auth_provider.g.dart
│       ├── screens/
│       │   └── login_screen.dart
│       └── widgets/
│           └── login_form.dart
```

### Entity 定义

```dart
// lib/features/auth/domain/entities/user.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String email,
    required String name,
    String? avatarUrl,
    @Default(false) bool isVerified,
  }) = _User;
}
```

### Repository 模式

```dart
// lib/features/auth/domain/repositories/auth_repository.dart
abstract class AuthRepository {
  Future<User> login(String email, String password);
  Future<void> logout();
  Future<User?> getCurrentUser();
  Stream<User?> watchUser();
}

// lib/features/auth/data/repositories/auth_repository_impl.dart
class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  final AuthLocalDataSource _localDataSource;

  AuthRepositoryImpl(this._remoteDataSource, this._localDataSource);

  @override
  Future<User> login(String email, String password) async {
    try {
      final userModel = await _remoteDataSource.login(email, password);
      await _localDataSource.cacheUser(userModel);
      return userModel.toEntity();
    } on DioException catch (e) {
      throw ServerException.fromDioError(e);
    }
  }

  @override
  Future<void> logout() async {
    await _localDataSource.clearCache();
    await _remoteDataSource.logout();
  }
}
```

## 状态管理模式

### Riverpod Provider

```dart
// lib/features/auth/presentation/providers/auth_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_provider.g.dart';

@riverpod
class Auth extends _$Auth {
  @override
  FutureOr<User?> build() {
    return ref.read(authRepositoryProvider).getCurrentUser();
  }

  Future<void> login(String email, String password) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final user = await ref.read(authRepositoryProvider).login(email, password);
      return user;
    });
  }

  Future<void> logout() async {
    await ref.read(authRepositoryProvider).logout();
    state = const AsyncData(null);
  }
}

// 简化的 Provider 定义
@riverpod
AuthRepository authRepository(AuthRepositoryRef ref) {
  return AuthRepositoryImpl(
    ref.read(authRemoteDataSourceProvider),
    ref.read(authLocalDataSourceProvider),
  );
}
```

### Consumer Widget 模式

```dart
// lib/features/auth/presentation/screens/login_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    ref.listen(authProvider, (previous, next) {
      if (next.hasError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.error.toString())),
        );
      }
    });

    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(controller: _emailController, decoration: InputDecoration(labelText: 'Email')),
            TextField(controller: _passwordController, decoration: InputDecoration(labelText: 'Password'), obscureText: true),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: authState.isLoading
                  ? null
                  : () => ref.read(authProvider.notifier).login(
                        _emailController.text,
                        _passwordController.text,
                      ),
              child: authState.isLoading
                  ? const CircularProgressIndicator()
                  : const Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 导航模式

### GoRouter 配置

```dart
// lib/app/routes/app_router.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/',
    redirect: (context, state) {
      final isLoggedIn = authState.valueOrNull != null;
      final isOnAuth = state.matchedLocation == '/login';

      if (!isLoggedIn && !isOnAuth) return '/login';
      if (isLoggedIn && isOnAuth) return '/';
      return null;
    },
    routes: [
      StatefulShellRoute.indexedStack(
        builder: (context, state, shell) => MainScaffold(shell: shell),
        branches: [
          StatefulShellBranch(routes: [
            GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
          ]),
          StatefulShellBranch(routes: [
            GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
          ]),
        ],
      ),
      GoRoute(path: '/login', builder: (_, __) => const LoginScreen()),
      GoRoute(
        path: '/detail/:id',
        builder: (_, state) => DetailScreen(id: state.pathParameters['id']!),
      ),
    ],
  );
});
```

### MainScaffold 实现

```dart
class MainScaffold extends StatelessWidget {
  final StatefulNavigationShell shell;
  const MainScaffold({super.key, required this.shell});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: shell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: shell.currentIndex,
        onDestinationSelected: (index) => shell.goBranch(index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
```

## 网络请求模式

### Dio 配置

```dart
// lib/core/network/api_client.dart
import 'package:dio/dio.dart';

class ApiClient {
  late final Dio _dio;

  ApiClient({required String baseUrl, required TokenStorage tokenStorage}) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 10),
    ));
    _dio.interceptors.addAll([
      AuthInterceptor(tokenStorage),
      LogInterceptor(requestBody: true, responseBody: true),
    ]);
  }

  Future<Response<T>> get<T>(String path, {Map<String, dynamic>? params}) =>
      _dio.get(path, queryParameters: params);

  Future<Response<T>> post<T>(String path, {dynamic data}) =>
      _dio.post(path, data: data);

  Future<Response<T>> put<T>(String path, {dynamic data}) =>
      _dio.put(path, data: data);

  Future<Response<T>> delete<T>(String path) => _dio.delete(path);
}

class AuthInterceptor extends Interceptor {
  final TokenStorage _tokenStorage;
  AuthInterceptor(this._tokenStorage);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _tokenStorage.getToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // 处理 token 刷新
    }
    handler.next(err);
  }
}
```

## 测试模式

### Unit Test

```dart
// test/unit/features/auth/usecases/login_usecase_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late LoginUseCase useCase;
  late MockAuthRepository mockRepository;

  setUp(() {
    mockRepository = MockAuthRepository();
    useCase = LoginUseCase(mockRepository);
  });

  test('should return user when login succeeds', () async {
    // Arrange
    final user = User(id: '1', email: 'test@test.com', name: 'Test');
    when(() => mockRepository.login('test@test.com', 'password'))
        .thenAnswer((_) async => user);

    // Act
    final result = await useCase('test@test.com', 'password');

    // Assert
    expect(result, user);
    verify(() => mockRepository.login('test@test.com', 'password')).called(1);
  });
}
```

### Widget Test

```dart
// test/widget/login_screen_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';

void main() {
  testWidgets('shows error message on login failure', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authRepositoryProvider.overrideWithValue(MockAuthRepository()),
        ],
        child: const MaterialApp(home: LoginScreen()),
      ),
    );

    await tester.enterText(find.byType(TextField).first, 'test@test.com');
    await tester.enterText(find.byType(TextField).last, 'wrong');
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    expect(find.text('Invalid credentials'), findsOneWidget);
  });
}
```

## 代码生成命令

```bash
# 运行所有代码生成
dart run build_runner build --delete-conflicting-outputs

# 监听文件变化自动生成
dart run build_runner watch --delete-conflicting-outputs

# 生成 Riverpod 代码
dart run riverpod_generator

# 生成 Freezed 代码
dart run build_runner build
```

## 常用 Widget 模式

### 响应式布局

```dart
class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;

  const ResponsiveLayout({super.key, required this.mobile, this.tablet, this.desktop});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth >= 1200) return desktop ?? tablet ?? mobile;
        if (constraints.maxWidth >= 600) return tablet ?? mobile;
        return mobile;
      },
    );
  }
}
```

### 加载状态处理

```dart
class AsyncValueWidget<T> extends StatelessWidget {
  final AsyncValue<T> value;
  final Widget Function(T data) data;
  final Widget Function(Object error, StackTrace stack)? error;
  final Widget? loading;

  const AsyncValueWidget({
    super.key,
    required this.value,
    required this.data,
    this.error,
    this.loading,
  });

  @override
  Widget build(BuildContext context) {
    return value.when(
      data: data,
      loading: () => loading ?? const Center(child: CircularProgressIndicator()),
      error: (e, st) => error?.call(e, st) ?? Center(child: Text('Error: $e')),
    );
  }
}
```
