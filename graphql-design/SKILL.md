---
name: graphql-design
description: |
  【GraphQL设计】设计 GraphQL Schema，包含类型定义、查询/变更设计、分页方案、错误处理、性能优化（N+1防护）。

  触发时机：
  - 用户要求"设计GraphQL API"、"GraphQL Schema"
  - 从 REST 迁移到 GraphQL
  - 需要优化 GraphQL 性能

  输出可执行的 Schema 定义。
category: development
---

# GraphQL Design — GraphQL API 设计技能

设计专业的 GraphQL Schema，包含最佳实践和性能优化。


## Goal

设计 GraphQL Schema，包含类型定义、查询/变更设计、分页方案、错误处理、性能优化（N+1防护）

## Trigger

- 用户要求"设计GraphQL API"、"GraphQL Schema"
  - 从 REST 迁移到 GraphQL
  - 需要优化 GraphQL 性能

## Workflow

```
输入 → 处理 → 输出
```
## Schema 设计原则

1. **类型优先** — 先设计 Schema，再实现 Resolver
2. **不可变设计** — 只暴露需要的数据，不要暴露内部实现
3. **分页规范** — 使用 Relay 风格的 Cursor 分页
4. **错误处理** — 使用 Union Type 处理业务错误
5. **性能防护** — 防止 N+1 查询和恶意深层嵌套

## 类型定义模板

```graphql
# scalar DateTime
scalar DateTime
scalar JSON

# 公共接口
interface Node {
  id: ID!
}

# 分页相关
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# 用户类型
type User implements Node {
  id: ID!
  email: String!
  name: String!
  avatar: String
  role: UserRole!
  createdAt: DateTime!
  updatedAt: DateTime!
  
  # 关联查询
  posts(first: Int, after: String): PostConnection!
  orders(first: Int, after: String): OrderConnection!
}

enum UserRole {
  ADMIN
  USER
  GUEST
}

# 帖子类型
type Post implements Node {
  id: ID!
  title: String!
  content: String!
  status: PostStatus!
  author: User!
  tags: [Tag!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

type Tag {
  id: ID!
  name: String!
}

# 分页 Connection
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  cursor: String!
  node: User!
}

type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PostEdge {
  cursor: String!
  node: Post!
}
```

## 查询设计

```graphql
type Query {
  # 单个资源查询
  user(id: ID!): User
  post(id: ID!): Post
  
  # 列表查询（带分页和过滤）
  users(
    first: Int
    after: String
    filter: UserFilter
    orderBy: UserOrderBy
  ): UserConnection!
  
  posts(
    first: Int
    after: String
    filter: PostFilter
    orderBy: PostOrderBy
  ): PostConnection!
  
  # 当前用户
  me: User
  
  # 搜索
  search(query: String!, types: [SearchType!]): SearchResult!
}

input UserFilter {
  role: UserRole
  email: String
  name: String
  createdAfter: DateTime
  createdBefore: DateTime
}

input PostFilter {
  status: PostStatus
  authorId: ID
  tagId: ID
  keyword: String
  createdAfter: DateTime
  createdBefore: DateTime
}

enum UserOrderBy {
  CREATED_AT_ASC
  CREATED_AT_DESC
  NAME_ASC
  NAME_DESC
}

enum PostOrderBy {
  CREATED_AT_ASC
  CREATED_AT_DESC
  TITLE_ASC
  TITLE_DESC
}
```

## 变更设计

```graphql
type Mutation {
  # 用户相关
  createUser(input: CreateUserInput!): CreateUserResult!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserResult!
  deleteUser(id: ID!): DeleteUserResult!
  
  # 帖子相关
  createPost(input: CreatePostInput!): CreatePostResult!
  updatePost(id: ID!, input: UpdateUserInput!): UpdatePostResult!
  publishPost(id: ID!): PublishPostResult!
  deletePost(id: ID!): DeletePostResult!
}

# 输入类型
input CreateUserInput {
  email: String!
  name: String!
  password: String!
  role: UserRole = USER
}

input UpdateUserInput {
  name: String
  email: String
  role: UserRole
}

# 结果类型（Union Type 处理成功和失败）
union CreateUserResult = CreateUserSuccess | ValidationError | ConflictError

type CreateUserSuccess {
  user: User!
}

type ValidationError {
  field: String!
  message: String!
}

type ConflictError {
  message: String!
  conflictingField: String!
}
```

## Resolver 实现（带 DataLoader 防 N+1）

```python
from strawberry.dataloader import DataLoader
from typing import List

# DataLoader 批量加载
async def load_users(user_ids: List[str]) -> List[User]:
    """批量加载用户，避免 N+1"""
    users = await db.users.find({"id": {"$in": user_ids}})
    user_map = {user.id: user for user in users}
    return [user_map.get(uid) for uid in user_ids]

async def load_posts_by_author(author_ids: List[str]) -> List[List[Post]]:
    """批量加载作者的帖子"""
    posts = await db.posts.find({"author_id": {"$in": author_ids}})
    posts_by_author = defaultdict(list)
    for post in posts:
        posts_by_author[post.author_id].append(post)
    return [posts_by_author.get(aid, []) for aid in author_ids]

@strawberry.type
class UserResolver:
    @strawberry.field
    async def posts(self, info: Info, first: int = 10, after: str = None) -> PostConnection:
        return await get_posts_connection(
            filter=PostFilter(authorId=self.id),
            first=first,
            after=after
        )

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, info: Info, id: str) -> User:
        return await info.context.user_loader.load(id)
    
    @strawberry.field
    async def users(
        self, info: Info,
        first: int = 10,
        after: str = None,
        filter: UserFilter = None,
        orderBy: UserOrderBy = None
    ) -> UserConnection:
        return await get_users_connection(filter, first, after, orderBy)
```

## 性能优化

### 1. 查询深度限制

```python
# 防止恶意深层嵌套查询
MAX_DEPTH = 5

def validate_query_depth(query: str) -> bool:
    depth = calculate_depth(query)
    return depth <= MAX_DEPTH
```

### 2. 查询复杂度分析

```python
# 为每个字段设置复杂度
COMPLEXITY_MAP = {
    "users": 1,
    "posts": 1,
    "user.posts": lambda args: args.get("first", 10),
}

def calculate_complexity(query: str) -> int:
    # 计算查询复杂度
    pass

MAX_COMPLEXITY = 1000
```

### 3. 响应缓存

```python
# 使用 DataLoader + Redis 缓存
class CachedDataLoader(DataLoader):
    def __init__(self, cache_key_prefix: str, ttl: int = 300):
        super().__init__(load_fn=self._load)
        self.cache_key_prefix = cache_key_prefix
        self.ttl = ttl
    
    async def _load(self, keys: List[str]) -> List:
        # 先查缓存
        cached = await redis.mget([f"{self.cache_key_prefix}:{k}" for k in keys])
        # 缓存未命中再查 DB
        # ...
```

## 错误处理

```graphql
# 使用 Union Type 而非抛出异常
union CreateUserResult = User | ValidationError | ConflictError | UnauthorizedError

# 客户端处理
mutation {
  createUser(input: {email: "test@example.com", name: "Test"}) {
    ... on User {
      id
      email
    }
    ... on ValidationError {
      field
      message
    }
    ... on ConflictError {
      message
    }
  }
}
```

## 快速使用

```
# 设计 GraphQL Schema
根据以下需求设计 GraphQL Schema：[粘贴需求]

# 从 REST 转换
将以下 REST API 转换为 GraphQL：[粘贴 REST 路由]

# 优化 N+1 问题
优化以下 Resolver 的 N+1 查询问题：[粘贴代码]

# 实现分页
为用户列表实现 Relay 风格的分页
```

## 参考资料

- Relay 分页规范: [references/relay-pagination.md](references/relay-pagination.md)
- N+1 问题解决: [references/dataloader.md](references/dataloader.md)
