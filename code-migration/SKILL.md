---
name: code-migration
description: |
  【代码迁移】框架迁移、语言升级、API 版本迁移的技术方案和执行指南。
  
  触发时机：
  - 用户要求"迁移代码"、"升级框架"、"Python 2到3"
  - 需要从旧框架迁移到新框架
  - API 版本需要升级
  
  提供迁移策略、步骤和验证方法。
category: development
---

# Code Migration


## Goal

框架迁移、语言升级、API 版本迁移的技术方案和执行指南

## Trigger

- 用户要求"迁移代码"、"升级框架"、"Python 2到3"
  - 需要从旧框架迁移到新框架
  - API 版本需要升级

## 目标

为代码迁移项目提供系统化的策略、执行步骤和验证方法，确保迁移过程可控、可回滚，最大程度降低风险。

## 工作流程

```
评估迁移范围 → 选择迁移策略 → 制定执行计划 → 分步迁移 → 验证 → 回滚预案
```

详见下方各迁移场景的具体指南。

## 触发条件

当用户需要：
- 将代码从旧框架迁移到新框架
- 升级编程语言版本（如 Python 2→3）
- 迁移 JavaScript 到 TypeScript
- 升级 API 版本
- 数据库 Schema 迁移

## 迁移策略

### 1. 绞杀者模式（Strangler Fig Pattern）

逐步替换旧系统组件，新旧系统并行运行，直到旧系统完全被替代。

```
┌─────────────────────────────────────────┐
│              负载均衡器 / 代理              │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│   新系统       │   │   旧系统       │
│ (逐步增加)     │   │ (逐步减少)     │
└───────────────┘   └───────────────┘
```

**适用场景**：
- 大型单体应用迁移
- 需要持续交付的系统
- 不能承受长时间停机

**执行步骤**：
1. 识别系统边界，定义迁移单元
2. 在新旧系统间设置路由层
3. 逐个功能迁移，每次迁移后验证
4. 旧功能下线，清理代码

### 2. 大爆炸模式（Big Bang）

一次性完成全部迁移。

**适用场景**：
- 小型项目或模块
- 新旧系统差异极大，无法并行
- 有充足的时间窗口

**风险**：
- 回滚困难
- 问题集中爆发
- 停机时间长

### 3. 并行运行模式（Parallel Run）

新旧系统同时运行，比对结果，确认无误后切换。

```
请求 ──┬──→ 旧系统 ──→ 结果 A ──┐
       │                        ├──→ 比对 ──→ 返回结果
       └──→ 新系统 ──→ 结果 B ──┘
```

**适用场景**：
- 金融、医疗等对正确性要求极高的系统
- 需要验证新系统行为一致性

## Python 2→3 迁移

### 迁移前准备

```bash
# 1. 代码分析
pip install pylint pyflakes
pylint --py2-only your_project/

# 2. 依赖检查
pip install caniusepython3
caniusepython3 -r requirements.txt

# 3. 测试覆盖率
pip install pytest pytest-cov
pytest --cov=your_project --cov-report=html
```

### 常见迁移模式

#### Print 语句

```python
# Python 2
print "Hello"
print "Name:", name

# Python 3
print("Hello")
print("Name:", name)
```

#### Unicode 处理

```python
# Python 2
s = u"字符串"
b = "字节"

# Python 3
s = "字符串"        # 默认 Unicode
b = b"字节"         # 明确字节
```

#### 除法运算

```python
# Python 2
5 / 2   # = 2
5 // 2  # = 2

# Python 3
5 / 2   # = 2.5
5 // 2  # = 2
```

#### 异常处理

```python
# Python 2
try:
    pass
except Exception, e:
    print e

# Python 3
try:
    pass
except Exception as e:
    print(e)
```

#### 字典方法

```python
# Python 2
for key in dict.keys():
    pass
for value in dict.values():
    pass
for key, value in dict.items():
    pass

# Python 3（相同，但返回视图而非列表）
for key in dict.keys():
    pass
```

### 自动化工具

```bash
# 使用 2to3 自动转换
2to3 -w -n your_project/

# 使用 futurize 渐进式迁移
pip install future
futurize -w your_project/

# 使用 pyupgrade 优化语法
pip install pyupgrade
pyupgrade --py3-plus *.py
```

## JavaScript→TypeScript 迁移

### 迁移策略

```
阶段 1：配置 TypeScript
  └── 添加 tsconfig.json，允许 JS/TS 混用

阶段 2：重命名文件
  └── .js → .ts/.tsx，添加 @ts-ignore

阶段 3：添加类型
  └── 逐步添加类型定义，移除 @ts-ignore

阶段 4：严格模式
  └── 启用 strict 模式，修复所有类型错误
```

### tsconfig.json 配置

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020", "DOM"],
    "jsx": "react-jsx",
    "strict": false,
    "esModuleInterop": true,
    "allowJs": true,
    "checkJs": false,
    "outDir": "./dist",
    "rootDir": "./src",
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

### 类型定义模式

```typescript
// types/api.ts
interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  createdAt: string;
}

// 从 JSDoc 迁移
/**
 * @param {string} name - 用户名
 * @returns {User} 用户对象
 */
function getUser(name) { ... }

// 迁移后
function getUser(name: string): User { ... }
```

### 渐进式类型添加

```typescript
// 1. 使用 any 作为占位符
function processData(data: any): any { ... }

// 2. 添加基本类型
function processData(data: Record<string, unknown>): unknown { ... }

// 3. 定义具体类型
interface ProcessInput { id: string; value: number; }
function processData(data: ProcessInput): ProcessResult { ... }
```

## Angular.js→Angular 迁移

### 迁移策略

```
1. 升级 Angular.js 到最新 1.x 版本
2. 引入组件化架构
3. 使用 ngUpgrade 并行运行
4. 逐模块迁移到 Angular
5. 移除 Angular.js 依赖
```

### ngUpgrade 混合模式

```typescript
// app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { UpgradeModule } from '@angular/upgrade/static';

@NgModule({
  imports: [BrowserModule, UpgradeModule],
  bootstrap: [] // 不自动引导
})
export class AppModule {
  constructor(private upgrade: UpgradeModule) {}

  ngDoBootstrap() {
    this.upgrade.bootstrap(document.body, ['legacyApp'], { strictDi: true });
  }
}
```

### 服务迁移示例

```javascript
// Angular.js 服务
angular.module('app').service('UserService', function($http) {
  this.getUser = function(id) {
    return $http.get('/api/users/' + id).then(function(response) {
      return response.data;
    });
  };
});
```

```typescript
// Angular 服务
@Injectable({ providedIn: 'root' })
export class UserService {
  constructor(private http: HttpClient) {}

  getUser(id: string): Observable<User> {
    return this.http.get<User>(`/api/users/${id}`);
  }
}
```

## jQuery→React/Vue 迁移

### 迁移策略

```
1. 分析 jQuery 代码，识别组件边界
2. 创建新框架项目
3. 逐个组件迁移
4. 使用 Web Components 或 iframe 集成
5. 移除 jQuery 依赖
```

### jQuery→React 对照

```javascript
// jQuery
$('#btn').on('click', function() {
  $.ajax({
    url: '/api/data',
    success: function(data) {
      $('#result').html(data.map(item => `<div>${item.name}</div>`).join(''));
    }
  });
});
```

```jsx
// React
function DataList() {
  const [data, setData] = useState([]);

  const handleClick = async () => {
    const response = await fetch('/api/data');
    const result = await response.json();
    setData(result);
  };

  return (
    <div>
      <button onClick={handleClick}>Load</button>
      <div>{data.map(item => <div key={item.id}>{item.name}</div>)}</div>
    </div>
  );
}
```

### jQuery→Vue 对照

```javascript
// jQuery
$('#form').on('submit', function(e) {
  e.preventDefault();
  var name = $('#name').val();
  var email = $('#email').val();
  // 验证和提交...
});
```

```vue
<!-- Vue 3 -->
<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="form.name" required />
    <input v-model="form.email" type="email" required />
    <button type="submit">Submit</button>
  </form>
</template>

<script setup>
import { reactive } from 'vue';

const form = reactive({ name: '', email: '' });

const handleSubmit = () => {
  // 验证和提交...
};
</script>
```

## API 版本迁移

### 版本控制策略

```
URL 路径版本：/api/v1/users, /api/v2/users
请求头版本：Accept: application/vnd.api.v2+json
查询参数：/api/users?version=2
```

### 渐进式迁移

```javascript
// 1. 路由层分发
app.use('/api/v1', v1Router);
app.use('/api/v2', v2Router);

// 2. 中间件转换
app.use('/api/v1/users', (req, res, next) => {
  // 转换请求格式
  req.body = transformV1ToV2(req.body);
  next();
}, v2UserController);

// 3. 响应适配器
function transformV2ToV1(response) {
  return {
    ...response,
    // 字段重命名等转换
  };
}
```

### 客户端迁移

```typescript
// API 客户端版本管理
class ApiClient {
  private version: string;

  constructor(version: string) {
    this.version = version;
  }

  async getUsers(): Promise<User[]> {
    const response = await fetch(`/api/${this.version}/users`);
    const data = await response.json();
    return this.version === 'v1' ? this.transformV1(data) : data;
  }

  private transformV1(data: any[]): User[] {
    return data.map(item => ({
      id: item.user_id,
      name: item.full_name,
      email: item.email_address,
    }));
  }
}
```

## 数据库 Schema 迁移

### 迁移工具

```bash
# Prisma
npx prisma migrate dev --name migration_name

# Alembic (Python)
alembic revision --autogenerate -m "migration_name"
alembic upgrade head

# Flyway (Java)
flyway migrate

# Knex.js
npx knex migrate:make migration_name
npx knex migrate:latest
```

### 迁移脚本模式

```sql
-- 添加列（不锁表）
ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT NULL;

-- 重命名列
ALTER TABLE users RENAME COLUMN name TO full_name;

-- 数据迁移
UPDATE users SET email = LOWER(TRIM(email)) WHERE email != LOWER(TRIM(email));

-- 添加索引（在线）
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

### 零停机迁移

```python
# 阶段 1：添加新列
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);

# 阶段 2：双写（应用层同时写入新旧列）
def update_user(user_id, data):
    db.execute("""
        UPDATE users 
        SET name = %s, full_name = %s 
        WHERE id = %s
    """, (data['name'], data['name'], user_id))

# 阶段 3：回填历史数据
UPDATE users SET full_name = name WHERE full_name IS NULL;

# 阶段 4：切换读取到新列
def get_user_name(user):
    return user.full_name

# 阶段 5：移除旧列
ALTER TABLE users DROP COLUMN name;
```

## 回滚策略

### 代码回滚

```bash
# Git 标记迁移版本
git tag pre-migration-v1.0

# 快速回滚
git revert HEAD
git push origin main
```

### 数据库回滚

```python
# Prisma 回滚
npx prisma migrate resolve --rolled-back migration_name

# Alembic 回滚
alembic downgrade -1

# 自定义回滚脚本
def rollback():
    db.execute("ALTER TABLE users DROP COLUMN full_name")
    db.execute("ALTER TABLE users RENAME COLUMN name_old TO name")
```

### 特性开关回滚

```typescript
// 使用特性开关控制新旧代码
const useNewFeature = featureFlags.isEnabled('new-feature');

if (useNewFeature) {
  return newImplementation();
} else {
  return legacyImplementation();
}
```

## 迁移验证

### 测试策略

```bash
# 1. 单元测试
pytest tests/ -v

# 2. 集成测试
pytest tests/integration/ -v

# 3. 契约测试
pact-verifier --provider-base-url=http://localhost:3000

# 4. 性能测试
k6 run performance-test.js

# 5. 数据一致性检查
python check_data_consistency.py
```

### 监控指标

```yaml
监控清单:
  - 错误率变化
  - 响应时间变化
  - 数据一致性
  - 功能完整性
  - 用户行为变化
```

## Example

```
用户: 将 Python 2 项目迁移到 Python 3

输出:
1. 分析依赖兼容性
2. 运行 2to3 工具
3. 修复 print 语句 → print()
4. 修复 unicode/str 处理
5. 更新 requirements.txt
6. 运行测试验证
```

## 最佳实践

1. **充分准备**：迁移前完成代码分析、依赖检查、测试覆盖
2. **小步快跑**：采用渐进式迁移，避免大爆炸式切换
3. **可回滚**：每一步都要有回滚方案
4. **并行运行**：新旧系统并行，验证无误后再切换
5. **监控告警**：迁移后密切关注系统指标
6. **文档记录**：记录迁移过程和决策
7. **团队沟通**：确保团队了解迁移计划和风险

## 边界情况

- **第三方依赖不兼容**：寻找替代库或编写适配器
- **数据格式变更**：编写数据转换脚本
- **性能下降**：迁移后进行性能测试和优化
- **安全漏洞**：迁移过程中注意安全问题
- **团队培训**：新技术栈需要团队学习时间
