# Framework Migration Reference

## Python 2→3 详细对照

### 语法变更

| 特性 | Python 2 | Python 3 |
|------|----------|----------|
| Print | `print "hi"` | `print("hi")` |
| 除法 | `5/2=2` | `5/2=2.5` |
| Unicode | `u"str"` | `"str"` |
| 字节 | `"bytes"` | `b"bytes"` |
| 异常 | `except E, e` | `except E as e` |
| xrange | `xrange(10)` | `range(10)` |
| dict.keys() | 返回列表 | 返回视图 |
| raw_input | `raw_input()` | `input()` |
| 整除 | `5/2=2` | `5//2=2` |

### 标准库变更

```python
# Python 2
import ConfigParser
import Queue
import cPickle
import httplib
import urllib2
import urlparse

# Python 3
import configparser
import queue
import pickle
import http.client
import urllib.request
import urllib.parse
```

### 兼容性写法

```python
# 使用 six 库
import six

if six.PY2:
    string_types = basestring
else:
    string_types = str

# 使用 future 库
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
```

## JavaScript→TypeScript 详细对照

### 类型定义模式

```typescript
// 基础类型
let name: string = "John";
let age: number = 30;
let isActive: boolean = true;
let items: string[] = ["a", "b"];
let data: [string, number] = ["John", 30];

// 接口
interface User {
  id: string;
  name: string;
  email?: string;  // 可选
  readonly createdAt: Date;  // 只读
}

// 类型别名
type Status = "pending" | "active" | "inactive";
type EventHandler = (event: Event) => void;

// 泛型
function identity<T>(arg: T): T {
  return arg;
}

// 联合类型
function process(value: string | number) { ... }

// 类型守卫
function isString(value: unknown): value is string {
  return typeof value === "string";
}
```

### 常见迁移模式

```javascript
// JavaScript - 动态类型
function createUser(data) {
  return {
    id: Date.now(),
    ...data,
    createdAt: new Date()
  };
}
```

```typescript
// TypeScript - 静态类型
interface CreateUserInput {
  name: string;
  email: string;
  role?: "admin" | "user";
}

interface User extends CreateUserInput {
  id: number;
  createdAt: Date;
}

function createUser(data: CreateUserInput): User {
  return {
    id: Date.now(),
    ...data,
    createdAt: new Date()
  };
}
```

### 类型断言迁移

```javascript
// JavaScript - 无类型检查
const user = getUser();
console.log(user.name.toUpperCase());
```

```typescript
// TypeScript - 类型断言
const user = getUser() as User;
console.log(user.name.toUpperCase());

// 或使用类型守卫
function assertUser(obj: unknown): asserts obj is User {
  if (!obj || typeof obj !== "object" || !("name" in obj)) {
    throw new Error("Not a User");
  }
}

const user = getUser();
assertUser(user);
console.log(user.name.toUpperCase());
```

## Angular.js→Angular 详细对照

### 指令迁移

```javascript
// Angular.js 指令
angular.module('app').directive('userCard', function() {
  return {
    restrict: 'E',
    scope: {
      user: '='
    },
    template: `
      <div class="card">
        <h3>{{user.name}}</h3>
        <p>{{user.email}}</p>
      </div>
    `,
    link: function(scope, element, attrs) {
      scope.$watch('user', function(newUser) {
        // 处理用户变化
      });
    }
  };
});
```

```typescript
// Angular 组件
@Component({
  selector: 'app-user-card',
  template: `
    <div class="card">
      <h3>{{ user.name }}</h3>
      <p>{{ user.email }}</p>
    </div>
  `
})
export class UserCardComponent implements OnInit, OnChanges {
  @Input() user!: User;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['user']) {
      // 处理用户变化
    }
  }
}
```

### 服务迁移

```javascript
// Angular.js 服务
angular.module('app').factory('UserService', function($http, $q) {
  return {
    getUsers: function() {
      var deferred = $q.defer();
      $http.get('/api/users').then(function(response) {
        deferred.resolve(response.data);
      }, function(error) {
        deferred.reject(error);
      });
      return deferred.promise;
    }
  };
});
```

```typescript
// Angular 服务
@Injectable({ providedIn: 'root' })
export class UserService {
  constructor(private http: HttpClient) {}

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>('/api/users').pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse) {
    return throwError(() => error);
  }
}
```

### 路由迁移

```javascript
// Angular.js 路由
angular.module('app').config(function($routeProvider) {
  $routeProvider
    .when('/users', {
      template: '<user-list></user-list>',
      controller: 'UserListController'
    })
    .when('/users/:id', {
      template: '<user-detail></user-detail>',
      controller: 'UserDetailController'
    })
    .otherwise({
      redirectTo: '/users'
    });
});
```

```typescript
// Angular 路由
const routes: Routes = [
  { path: 'users', component: UserListComponent },
  { path: 'users/:id', component: UserDetailComponent },
  { path: '', redirectTo: '/users', pathMatch: 'full' },
  { path: '**', component: NotFoundComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
```

## jQuery→React 详细对照

### DOM 操作迁移

```javascript
// jQuery
$('#button').click(function() {
  $('.container').addClass('active');
  $('input').val('').focus();
  $.ajax({
    url: '/api/data',
    success: function(data) {
      $('#result').html(data);
    }
  });
});
```

```jsx
// React
function MyComponent() {
  const [isActive, setIsActive] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [result, setResult] = useState('');

  const handleClick = async () => {
    setIsActive(true);
    setInputValue('');
    inputRef.current?.focus();
    
    const response = await fetch('/api/data');
    const data = await response.text();
    setResult(data);
  };

  return (
    <div className={isActive ? 'active' : ''}>
      <button onClick={handleClick}>Click</button>
      <input
        ref={inputRef}
        value={inputValue}
        onChange={e => setInputValue(e.target.value)}
      />
      <div dangerouslySetInnerHTML={{ __html: result }} />
    </div>
  );
}
```

### 事件处理迁移

```javascript
// jQuery - 事件委托
$(document).on('click', '.item', function() {
  var id = $(this).data('id');
  // 处理点击
});

// jQuery - 自定义事件
$('#element').trigger('customEvent', { data: 'value' });
$('#element').on('customEvent', function(e, data) {
  console.log(data);
});
```

```jsx
// React - 事件处理
function ItemList({ items, onItemClick }) {
  return (
    <div>
      {items.map(item => (
        <div
          key={item.id}
          data-id={item.id}
          onClick={() => onItemClick(item.id)}
        >
          {item.name}
        </div>
      ))}
    </div>
  );
}

// React - 自定义事件通过 props
function Parent() {
  const handleCustomEvent = (data) => {
    console.log(data);
  };

  return <Child onCustomEvent={handleCustomEvent} />;
}
```

### 动画迁移

```javascript
// jQuery 动画
$('.element').fadeIn(300);
$('.element').slideUp(200);
$('.element').animate({ left: '200px' }, 500);
```

```jsx
// React + CSS 过渡
function AnimatedComponent({ isVisible }) {
  return (
    <div className={`element ${isVisible ? 'visible' : 'hidden'}`}>
      Content
    </div>
  );
}

// CSS
.element {
  transition: opacity 300ms, transform 200ms;
}
.element.visible {
  opacity: 1;
  transform: translateY(0);
}
.element.hidden {
  opacity: 0;
  transform: translateY(-20px);
}
```

## jQuery→Vue 详细对照

### 响应式数据

```javascript
// jQuery - 手动更新 DOM
var count = 0;
$('#counter').text(count);
$('#increment').click(function() {
  count++;
  $('#counter').text(count);
});
```

```vue
<!-- Vue 3 - 响应式 -->
<template>
  <div>
    <span>{{ count }}</span>
    <button @click="increment">Increment</button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const count = ref(0);
const increment = () => count.value++;
</script>
```

### 表单处理

```javascript
// jQuery
$('#myForm').submit(function(e) {
  e.preventDefault();
  var formData = {
    name: $('#name').val(),
    email: $('#email').val(),
    agree: $('#agree').is(':checked')
  };
  
  $.post('/api/submit', formData, function(response) {
    $('#message').text('Success!');
  });
});
```

```vue
<!-- Vue 3 -->
<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="form.name" required />
    <input v-model="form.email" type="email" required />
    <input v-model="form.agree" type="checkbox" />
    <button type="submit">Submit</button>
    <p v-if="message">{{ message }}</p>
  </form>
</template>

<script setup>
import { reactive, ref } from 'vue';

const form = reactive({
  name: '',
  email: '',
  agree: false
});
const message = ref('');

const handleSubmit = async () => {
  const response = await fetch('/api/submit', {
    method: 'POST',
    body: JSON.stringify(form)
  });
  message.value = 'Success!';
};
</script>
```

## API 版本迁移详细对照

### REST API 版本控制

```yaml
# OpenAPI 3.0 - 多版本定义
openapi: 3.0.0
info:
  title: My API
  version: 2.0.0

paths:
  /api/v2/users:
    get:
      summary: Get users (v2)
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/UserV2'

components:
  schemas:
    UserV1:
      type: object
      properties:
        user_id:
          type: string
        full_name:
          type: string
        email_address:
          type: string

    UserV2:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
```

### GraphQL 版本迁移

```graphql
# V1 Schema
type User {
  user_id: ID!
  full_name: String!
  email_address: String!
}

# V2 Schema (废弃旧字段)
type User {
  id: ID!
  name: String!
  email: String!
  
  # 废弃但保留兼容性
  user_id: ID! @deprecated(reason: "Use id instead")
  full_name: String! @deprecated(reason: "Use name instead")
  email_address: String! @deprecated(reason: "Use email instead")
}
```

### 版本协商

```typescript
// 客户端版本协商
class ApiClient {
  private preferredVersion = 'v2';

  async request(endpoint: string, options?: RequestInit) {
    const response = await fetch(endpoint, {
      ...options,
      headers: {
        ...options?.headers,
        'Accept': `application/vnd.api.${this.preferredVersion}+json`,
        'X-API-Version': this.preferredVersion
      }
    });

    // 检查服务器支持的版本
    const serverVersion = response.headers.get('X-API-Version');
    if (serverVersion !== this.preferredVersion) {
      console.warn(`Server returned version ${serverVersion}, expected ${this.preferredVersion}`);
    }

    return response.json();
  }
}
```
