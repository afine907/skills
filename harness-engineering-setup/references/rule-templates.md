# 规则文件模板

本文档提供各技术栈的规则模板，用于快速生成 .claude/rules/ 文件。

## 通用规则模板

### code-style.md

```markdown
---
globs: ["src/**/*", "lib/**/*"]
---

# 代码风格规范

## 命名约定

- **变量/函数**: 使用 camelCase（JavaScript/TypeScript）或 snake_case（Python）
- **类/组件**: 使用 PascalCase
- **常量**: 使用 UPPER_SNAKE_CASE
- **文件名**: 使用 kebab-case（JavaScript）或 snake_case（Python）

## 格式化

- 使用项目配置的格式化工具（Prettier/Black）
- 缩进：2 空格（JavaScript/TypeScript）或 4 空格（Python）
- 行长度：不超过 100 字符

## 导入顺序

1. 内置模块（fs, path 等）
2. 外部包（react, express 等）
3. 内部模块（./utils, ../services 等）
4. 样式文件（.css, .scss 等）

## 注释

- 函数必须有 JSDoc/docstring 注释
- 复杂逻辑添加行内注释
- 避免无意义注释（// 设置名字）
```

### git.md

```markdown
---
globs: ["**/*"]
---

# Git 工作流规范

## 提交信息

使用 Conventional Commits 格式：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**类型：**
- feat: 新功能
- fix: 修复 bug
- docs: 文档更新
- style: 代码格式（不影响功能）
- refactor: 重构
- test: 添加测试
- chore: 构建/工具更新

## 分支命名

- `feature/<name>` - 新功能
- `fix/<name>` - 修复
- `hotfix/<name>` - 紧急修复
- `release/<version>` - 发布分支

## PR 规范

- 标题使用 Conventional Commits 格式
- 描述变更内容和原因
- 关联相关 issue
- 请求至少一人审查
```

### documentation.md

```markdown
---
globs: ["**/*"]
---

# 文档规范

## 代码文档

- 公共 API 必须有文档注释
- 复杂算法添加实现说明
- 记录非显而易见的设计决策

## README 结构

1. 项目标题和简短描述
2. 安装说明
3. 使用示例
4. API 文档（如适用）
5. 贡献指南
6. 许可证

## 变更日志

遵循 Keep a Changelog 格式：
- Added: 新功能
- Changed: 已有功能变更
- Deprecated: 即将移除的功能
- Removed: 已移除的功能
- Fixed: Bug 修复
- Security: 安全相关变更
```

## TypeScript 规则模板

### typescript.md

```markdown
---
globs: ["src/**/*.ts", "src/**/*.tsx"]
---

# TypeScript 规范

## 类型安全

- 禁止使用 `any` 类型，使用 `unknown` 替代
- 优先使用接口（interface）定义对象结构
- 使用泛型提高代码复用性
- 为函数参数和返回值添加类型注解

## 工具类型

善用 TypeScript 内置工具类型：
```typescript
// 使用 Partial 表示可选属性
interface UserUpdate extends Partial<User> {}

// 使用 Pick 提取部分属性
type UserPreview = Pick<User, 'id' | 'name'>

// 使用 Omit 排除属性
type UserWithoutEmail = Omit<User, 'email'>
```

## 错误处理

```typescript
// 使用自定义错误类型
class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'AppError';
  }
}

// 使用 Result 模式处理可能失败的操作
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };
```

## 异步处理

```typescript
// 优先使用 async/await
async function getUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new AppError('User not found', 'USER_NOT_FOUND', 404);
  }
  return response.json();
}

// 错误处理使用 try/catch
try {
  const user = await getUser('123');
} catch (error) {
  if (error instanceof AppError) {
    console.error(`Error ${error.code}: ${error.message}`);
  }
}
```

## 测试

```typescript
// 使用描述性测试名称
describe('UserService', () => {
  describe('getUser', () => {
    it('should return user when valid id provided', async () => {
      // Arrange
      const userId = '123';
      
      // Act
      const user = await getUser(userId);
      
      // Assert
      expect(user).toBeDefined();
      expect(user.id).toBe(userId);
    });

    it('should throw AppError when user not found', async () => {
      // Arrange
      const userId = 'nonexistent';
      
      // Act & Assert
      await expect(getUser(userId)).rejects.toThrow(AppError);
    });
  });
});
```

## 参考资源

- TypeScript 官方文档
- TypeScript Deep Dive
- Effective TypeScript
```

## Python 规则模板

### python.md

```markdown
---
globs: ["**/*.py"]
---

# Python 规范

## 代码风格

遵循 PEP 8 规范：
- 使用 4 空格缩进
- 行长度不超过 79 字符（代码）或 72 字符（注释）
- 使用 snake_case 命名函数和变量
- 使用 PascalCase 命名类

## 类型提示

为所有公共函数添加类型提示：

```python
from typing import Optional, List
from datetime import datetime

def get_user(
    user_id: int,
    include_deleted: bool = False
) -> Optional[User]:
    """获取用户信息
    
    Args:
        user_id: 用户 ID
        include_deleted: 是否包含已删除用户
        
    Returns:
        用户对象，如果不存在则返回 None
    """
    pass

def process_items(items: List[str]) -> dict[str, int]:
    """处理项目列表
    
    Args:
        items: 要处理的项目列表
        
    Returns:
        处理结果统计
    """
    pass
```

## 异步编程

使用 asyncio 进行异步操作：

```python
import asyncio
from aiohttp import ClientSession

async def fetch_data(url: str) -> dict:
    """异步获取数据"""
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_multiple_urls(urls: list[str]) -> list[dict]:
    """并发处理多个 URL"""
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)
```

## 错误处理

```python
# 使用自定义异常
class AppError(Exception):
    """应用基础异常"""
    def __init__(self, message: str, code: str, status_code: int = 500):
        super().__init__(message)
        self.code = code
        self.status_code = status_code

class NotFoundError(AppError):
    """资源未找到异常"""
    def __init__(self, resource: str, resource_id: any):
        super().__init__(
            f"{resource} with id {resource_id} not found",
            f"{resource.upper()}_NOT_FOUND",
            404
        )

# 使用上下文管理器处理资源
class DatabaseConnection:
    def __enter__(self):
        self.connection = create_connection()
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
```

## 测试

使用 pytest 进行测试：

```python
import pytest
from unittest.mock import Mock, patch

class TestUserService:
    """用户服务测试"""
    
    @pytest.fixture
    def user_service(self):
        """创建用户服务实例"""
        return UserService()
    
    @pytest.fixture
    def sample_user(self):
        """示例用户数据"""
        return {"id": 1, "name": "Test User", "email": "test@example.com"}
    
    def test_get_user_success(self, user_service, sample_user):
        """测试成功获取用户"""
        # Arrange
        user_id = 1
        
        # Act
        user = user_service.get_user(user_id)
        
        # Assert
        assert user is not None
        assert user["id"] == user_id
    
    def test_get_user_not_found(self, user_service):
        """测试用户不存在"""
        # Arrange
        user_id = 999
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            user_service.get_user(user_id)
    
    @patch('database.get_user')
    def test_get_user_with_mock(self, mock_get_user, user_service):
        """使用 mock 测试用户获取"""
        # Arrange
        mock_get_user.return_value = {"id": 1, "name": "Mock User"}
        
        # Act
        user = user_service.get_user(1)
        
        # Assert
        assert user["name"] == "Mock User"
        mock_get_user.assert_called_once_with(1)
```

## 项目结构

推荐的项目结构：
```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   └── services/
│       ├── __init__.py
│       └── user_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_user_service.py
├── pyproject.toml
└── README.md
```

## 参考资源

- PEP 8 -- Style Guide for Python Code
- Python Type Hints
- pytest Documentation
- Real Python Testing Tutorial
```

## Go 规则模板

### go.md

```markdown
---
globs: ["**/*.go"]
---

# Go 规范

## 代码风格

遵循 Go 标准格式（gofmt）：
- 使用 gofmt 自动格式化
- 使用 golangci-lint 进行代码检查
- 遵循 Effective Go 指南

## 命名约定

```go
// 导出函数使用 PascalCase
func GetUserByID(id int) (*User, error) {
    // 实现
}

// 非导出函数使用 camelCase
func validateEmail(email string) bool {
    // 实现
}

// 接口命名以 -er 结尾
type Reader interface {
    Read(p []byte) (n int, err error)
}

// 常量使用 PascalCase 或 UPPER_SNAKE_CASE
const MaxRetries = 3
const DEFAULT_TIMEOUT = 30
```

## 错误处理

```go
// 使用自定义错误类型
type AppError struct {
    Code       string `json:"code"`
    Message    string `json:"message"`
    StatusCode int    `json:"-"`
}

func (e *AppError) Error() string {
    return e.Message
}

func NewNotFoundError(resource string, id any) *AppError {
    return &AppError{
        Code:       "NOT_FOUND",
        Message:    fmt.Sprintf("%s with id %v not found", resource, id),
        StatusCode: 404,
    }
}

// 错误处理模式
func GetUser(id int) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, NewNotFoundError("user", id)
        }
        return nil, fmt.Errorf("failed to get user: %w", err)
    }
    return user, nil
}
```

## 并发处理

```go
// 使用 context 控制超时
func ProcessWithTimeout(ctx context.Context, data []byte) error {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    
    select {
    case <-ctx.Done():
        return ctx.Err()
    case result := <-processAsync(data):
        return result.Err
    }
}

// 使用 sync.WaitGroup 等待多个 goroutine
func ProcessItems(items []Item) []Result {
    var wg sync.WaitGroup
    results := make([]Result, len(items))
    
    for i, item := range items {
        wg.Add(1)
        go func(i int, item Item) {
            defer wg.Done()
            results[i] = processItem(item)
        }(i, item)
    }
    
    wg.Wait()
    return results
}
```

## 测试

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestGetUser(t *testing.T) {
    // Arrange
    service := NewUserService()
    userID := 1
    
    // Act
    user, err := service.GetUser(userID)
    
    // Assert
    require.NoError(t, err)
    assert.Equal(t, userID, user.ID)
    assert.NotEmpty(t, user.Name)
}

func TestGetUser_NotFound(t *testing.T) {
    // Arrange
    service := NewUserService()
    userID := 999
    
    // Act
    user, err := service.GetUser(userID)
    
    // Assert
    assert.Nil(t, user)
    assert.Error(t, err)
    assert.True(t, errors.As(err, &NotFoundError{}))
}

func BenchmarkGetUser(b *testing.B) {
    service := NewUserService()
    
    for i := 0; i < b.N; i++ {
        service.GetUser(1)
    }
}
```

## 项目结构

推荐的 Go 项目结构：
```
project/
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── config/
│   │   └── config.go
│   ├── handler/
│   │   └── user_handler.go
│   ├── model/
│   │   └── user.go
│   ├── repository/
│   │   └── user_repository.go
│   └── service/
│       └── user_service.go
├── pkg/
│   └── middleware/
│       └── auth.go
├── go.mod
├── go.sum
├── Makefile
└── README.md
```

## 参考资源

- Effective Go
- Go Code Review Comments
- Go Testing Patterns
```

## React 规则模板

### react.md

```markdown
---
globs: ["src/**/*.tsx", "src/**/*.jsx"]
---

# React 规范

## 组件设计

```tsx
// 使用函数组件和 Hooks
interface UserCardProps {
  user: User;
  onSelect: (userId: string) => void;
}

export function UserCard({ user, onSelect }: UserCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="user-card">
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      <button onClick={() => onSelect(user.id)}>
        Select
      </button>
    </div>
  );
}
```

## 状态管理

```tsx
// 使用 Zustand 进行状态管理
import { create } from 'zustand';

interface UserStore {
  users: User[];
  loading: boolean;
  error: string | null;
  fetchUsers: () => Promise<void>;
  addUser: (user: User) => void;
}

export const useUserStore = create<UserStore>((set) => ({
  users: [],
  loading: false,
  error: null,
  
  fetchUsers: async () => {
    set({ loading: true, error: null });
    try {
      const users = await api.getUsers();
      set({ users, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },
  
  addUser: (user) => set((state) => ({
    users: [...state.users, user]
  })),
}));
```

## 性能优化

```tsx
// 使用 React.memo 避免不必要的重渲染
export const UserCard = React.memo(function UserCard({ 
  user, 
  onSelect 
}: UserCardProps) {
  return (
    <div className="user-card">
      <h3>{user.name}</h3>
      <button onClick={() => onSelect(user.id)}>
        Select
      </button>
    </div>
  );
});

// 使用 useMemo 缓存计算结果
const sortedUsers = useMemo(() => {
  return users.sort((a, b) => a.name.localeCompare(b.name));
}, [users]);

// 使用 useCallback 缓存函数引用
const handleSelect = useCallback((userId: string) => {
  onSelect(userId);
}, [onSelect]);
```

## 错误处理

```tsx
// 使用 Error Boundary 捕获组件错误
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

// 使用 Suspense 处理异步组件
<Suspense fallback={<Loading />}>
  <AsyncComponent />
</Suspense>
```

## 测试

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { UserCard } from './UserCard';

describe('UserCard', () => {
  const mockUser = {
    id: '1',
    name: 'Test User',
    email: 'test@example.com'
  };
  
  const mockOnSelect = jest.fn();
  
  it('renders user information', () => {
    render(<UserCard user={mockUser} onSelect={mockOnSelect} />);
    
    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
  });
  
  it('calls onSelect when button clicked', () => {
    render(<UserCard user={mockUser} onSelect={mockOnSelect} />);
    
    fireEvent.click(screen.getByRole('button', { name: /select/i }));
    
    expect(mockOnSelect).toHaveBeenCalledWith('1');
  });
});
```

## 项目结构

推荐的 React 项目结构：
```
src/
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   └── Input.tsx
│   └── features/
│       ├── user/
│       │   ├── UserCard.tsx
│       │   └── UserList.tsx
│       └── auth/
│           ├── LoginForm.tsx
│           └── RegisterForm.tsx
├── hooks/
│   ├── useAuth.ts
│   └── useUsers.ts
├── stores/
│   ├── authStore.ts
│   └── userStore.ts
├── services/
│   ├── api.ts
│   └── auth.ts
├── types/
│   └── user.ts
└── utils/
    └── helpers.ts
```

## 参考资源

- React 官方文档
- React TypeScript Cheatsheet
- Testing React Apps
```

## API 设计规则模板

### api-design.md

```markdown
---
globs: ["src/routes/**/*", "src/api/**/*", "api/**/*"]
---

# API 设计规范

## RESTful 设计

```
GET    /api/users          # 获取用户列表
GET    /api/users/:id      # 获取单个用户
POST   /api/users          # 创建用户
PUT    /api/users/:id      # 更新用户
DELETE /api/users/:id      # 删除用户

GET    /api/users/:id/posts  # 获取用户的帖子
```

## 请求/响应格式

```typescript
// 请求体
interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
}

// 响应体
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  meta?: {
    page: number;
    limit: number;
    total: number;
  };
}

// 成功响应
{
  "success": true,
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  }
}

// 错误响应
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": "Invalid email format"
    }
  }
}
```

## 状态码使用

```
200 OK                    # 成功
201 Created               # 创建成功
204 No Content            # 删除成功
400 Bad Request           # 请求参数错误
401 Unauthorized          # 未认证
403 Forbidden             # 无权限
404 Not Found             # 资源不存在
409 Conflict              # 资源冲突
422 Unprocessable Entity  # 数据验证失败
429 Too Many Requests     # 请求过多
500 Internal Server Error # 服务器错误
```

## 分页

```typescript
// 请求参数
interface PaginationParams {
  page?: number;    // 页码，默认 1
  limit?: number;   // 每页数量，默认 10，最大 100
  sort?: string;    // 排序字段
  order?: 'asc' | 'desc';  // 排序方向
}

// 响应中的分页信息
interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

// 使用示例
GET /api/users?page=2&limit=20&sort=created_at&order=desc

// 响应
{
  "success": true,
  "data": [...],
  "meta": {
    "page": 2,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

## 认证与授权

```typescript
// JWT Token 验证中间件
async function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({
      success: false,
      error: {
        code: 'UNAUTHORIZED',
        message: 'No token provided'
      }
    });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      error: {
        code: 'INVALID_TOKEN',
        message: 'Token is invalid or expired'
      }
    });
  }
}

// 角色验证中间件
function requireRole(...roles: string[]) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        error: {
          code: 'FORBIDDEN',
          message: 'Insufficient permissions'
        }
      });
    }
    next();
  };
}
```

## 速率限制

```typescript
// 使用 express-rate-limit
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100,  // 每个 IP 最多 100 个请求
  message: {
    success: false,
    error: {
      code: 'TOO_MANY_REQUESTS',
      message: 'Too many requests, please try again later'
    }
  }
});

app.use('/api/', apiLimiter);
```

## 文档

使用 OpenAPI/Swagger 记录 API：

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /api/users:
    get:
      summary: 获取用户列表
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

## 参考资源

- RESTful API Design Best Practices
- HTTP Status Codes
- OpenAPI Specification
```

## 测试规则模板

### testing.md

```markdown
---
globs: ["**/*.test.ts", "**/*.test.tsx", "**/*.test.js", "**/*.test.jsx", "**/*.spec.ts", "**/*.spec.tsx", "**/*.spec.js", "**/*.spec.jsx", "**/__tests__/**"]
---

# 测试规范

## 测试框架

### JavaScript/TypeScript
- **单元测试**: Vitest (推荐) 或 Jest
- **组件测试**: React Testing Library
- **端到端测试**: Playwright 或 Cypress
- **覆盖率**: c8 (Vitest) 或 istanbul (Jest)

### Python
- **单元测试**: pytest
- **模拟**: pytest-mock
- **覆盖率**: pytest-cov
- **异步测试**: pytest-asyncio

### Go
- **单元测试**: go test + testify
- **模拟**: gomock 或 mockery
- **覆盖率**: go test -cover
- **HTTP 测试**: net/http/httptest

## 测试命名规范

### 文件命名
- 测试文件与源文件同目录
- 使用 `.test.ts`, `.test.tsx`, `.spec.ts` 后缀
- Python 使用 `test_*.py` 前缀
- Go 使用 `*_test.go` 后缀

### 测试描述
```typescript
// 好的测试描述
describe('UserService', () => {
  describe('getUser', () => {
    it('should return user when valid id provided', () => {})
    it('should throw NotFoundError when user does not exist', () => {})
    it('should handle database connection errors', () => {})
  })
})

// 不好的测试描述
describe('UserService', () => {
  it('test getUser', () => {})  // 太笼统
  it('works', () => {})  // 无意义
})
```

## 测试结构

### AAA 模式 (Arrange, Act, Assert)
```typescript
it('should calculate total price correctly', () => {
  // Arrange
  const items = [
    { name: 'Item 1', price: 10 },
    { name: 'Item 2', price: 20 }
  ];
  const taxRate = 0.1;

  // Act
  const total = calculateTotal(items, taxRate);

  // Assert
  expect(total).toBe(33);
});
```

### Given-When-Then 模式
```python
def test_calculate_total_with_tax():
    # Given
    items = [
        {"name": "Item 1", "price": 10},
        {"name": "Item 2", "price": 20}
    ]
    tax_rate = 0.1

    # When
    total = calculate_total(items, tax_rate)

    # Then
    assert total == 33
```

## 测试覆盖率

### 覆盖率目标
- **行覆盖率**: >= 80%
- **分支覆盖率**: >= 70%
- **函数覆盖率**: >= 90%

### 覆盖率工具配置

**Vitest (TypeScript)**:
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/**/*.d.ts',
        'src/**/*.config.*'
      ]
    }
  }
});
```

**pytest (Python)**:
```ini
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError"
]
```

## 测试最佳实践

### 1. 测试行为，不是实现
```typescript
// 好：测试行为
it('should display user name when logged in', () => {
  render(<UserProfile user={mockUser} />);
  expect(screen.getByText('John Doe')).toBeInTheDocument();
});

// 不好：测试实现
it('should call setUserState when componentDidMount', () => {
  const spy = jest.spyOn(UserProfile.prototype, 'componentDidMount');
  render(<UserProfile user={mockUser} />);
  expect(spy).toHaveBeenCalled();
});
```

### 2. 使用 Mock 隔离依赖
```typescript
// Mock 外部依赖
jest.mock('./api', () => ({
  fetchUser: jest.fn(),
}));

// Mock 模块
jest.mock('node-fetch');

// 部分 Mock
jest.mock('./utils', () => ({
  ...jest.requireActual('./utils'),
  formatDate: jest.fn(),
}));
```

### 3. 测试边界情况
```typescript
describe('validateEmail', () => {
  it('should return true for valid email', () => {
    expect(validateEmail('test@example.com')).toBe(true);
  });

  it('should return false for empty string', () => {
    expect(validateEmail('')).toBe(false);
  });

  it('should return false for invalid format', () => {
    expect(validateEmail('invalid-email')).toBe(false);
  });

  it('should handle null gracefully', () => {
    expect(validateEmail(null)).toBe(false);
  });
});
```

### 4. 测试异步代码
```typescript
// async/await
it('should fetch user data', async () => {
  const user = await fetchUser('123');
  expect(user).toBeDefined();
  expect(user.id).toBe('123');
});

// Promise
it('should fetch user data', () => {
  return fetchUser('123').then(user => {
    expect(user).toBeDefined();
  });
});

// React Testing Library
it('should load user on mount', async () => {
  render(<UserProfile userId="123" />);
  expect(await screen.findByText('John Doe')).toBeInTheDocument();
});
```

## 测试工具

### 测试运行命令

**JavaScript/TypeScript**:
```bash
# 运行所有测试
npm test

# 运行特定文件
npm test -- UserService.test.ts

# 运行覆盖率
npm run test:coverage

# 监听模式
npm run test:watch
```

**Python**:
```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_user_service.py

# 运行特定测试
pytest tests/test_user_service.py::test_get_user

# 运行覆盖率
pytest --cov=src --cov-report=html
```

**Go**:
```bash
# 运行所有测试
go test ./...

# 运行特定包
go test ./internal/service/...

# 运行特定测试
go test -run TestGetUser ./internal/service/...

# 运行覆盖率
go test -cover ./...
```

### 测试辅助工具

**测试数据工厂**:
```typescript
// factory.ts
export const createMockUser = (overrides?: Partial<User>): User => ({
  id: '1',
  name: 'Test User',
  email: 'test@example.com',
  ...overrides,
});

export const createMockPost = (overrides?: Partial<Post>): Post => ({
  id: '1',
  title: 'Test Post',
  content: 'Test content',
  authorId: '1',
  ...overrides,
});
```

**测试工具函数**:
```python
# tests/utils.py
import pytest
from typing import Any, Dict

def create_mock_user(**kwargs) -> Dict[str, Any]:
    """创建模拟用户数据"""
    return {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        **kwargs
    }

def assert_response_status(response, status_code: int):
    """断言响应状态码"""
    assert response.status_code == status_code, \
        f"Expected {status_code}, got {response.status_code}"
```

## 参考资源

- Testing JavaScript by Kent C. Dodds
- Python Testing with pytest
- Go Testing Cookbook
- React Testing Library Docs
```
