---
name: graphql-design
description: |
  【GraphQL设计】设计 GraphQL Schema，包含类型定义、查询/变更设计、分页方案、错误处理、性能优化。

  触发时机：
  - 用户要求"设计GraphQL API"、"GraphQL Schema"
  - 从 REST 迁移到 GraphQL
  - 需要优化 GraphQL 性能
category: development
---

# GraphQL Design — GraphQL API 设计

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow

设计专业的 GraphQL Schema，包含最佳实践和性能优化。

## Workflow

1. **分析需求** — 识别实体、关系、操作
2. **设计 Schema** — 类型、Query、Mutation、Subscription
3. **实现解析器** — Resolver 函数、数据加载
4. **优化性能** — N+1 防护、缓存、分页
5. **错误处理** — 统一错误格式、权限校验

## Schema 设计

```graphql
# 用户类型

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
type User {
  id: ID!
  email: String!
  name: String!
  posts: [Post!]!       # 关联查询
  createdAt: DateTime!
}

# 文章类型

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  status: PostStatus!
}

enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

# 查询

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
type Query {
  user(id: ID!): User
  users(first: Int, after: String): UserConnection!  # 游标分页
  post(id: ID!): Post
  posts(filter: PostFilter, first: Int, after: String): PostConnection!
}

# 变更

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  createPost(input: CreatePostInput!): Post!
  publishPost(id: ID!): Post!
}

# 输入类型

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
input CreateUserInput {
  email: String!
  name: String!
}

input PostFilter {
  status: PostStatus
  authorId: ID
  keyword: String
}
```

## 游标分页 (Relay 规范)

```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  cursor: String!
  node: User!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

## N+1 防护 (DataLoader)

```python
from aiodataloader import DataLoader

class UserLoader(DataLoader):
    async def batch_load_fn(self, user_ids):
        users = await db.fetch("SELECT * FROM users WHERE id = ANY($1)", user_ids)
        user_map = {u.id: u for u in users}
        return [user_map.get(uid) for uid in user_ids]

# 在 Resolver 中使用

## Goal

## Trigger

见 description 中的触发时机

见 ## Workflow
async def resolve_posts(parent, info):
    loader = info.context["user_loader"]
    return await loader.load(parent.author_id)
```

## Example

```
用户: 设计一个博客系统的 GraphQL API

输出:
schema:
  - User, Post, Comment 类型
  - Query: user, users, post, posts (带过滤和分页)
  - Mutation: createUser, createPost, publishPost, addComment
  - 游标分页 (Relay 规范)
  - DataLoader 防 N+1
  - 统一错误格式
```

## 参考

- DataLoader: [references/dataloader.md](references/dataloader.md)
- Relay 分页: [references/relay-pagination.md](references/relay-pagination.md)
