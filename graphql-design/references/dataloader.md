# DataLoader Reference

## The N+1 Problem

Without DataLoader, GraphQL resolvers cause excessive database queries:

```
query {
  users {         # 1 query: SELECT * FROM users
    posts {       # N queries: SELECT * FROM posts WHERE user_id = ?
      comments {  # N*M queries: SELECT * FROM comments WHERE post_id = ?
        author {  # N*M*K queries: SELECT * FROM users WHERE id = ?
          name
        }
      }
    }
  }
}
```

DataLoader batches these into efficient queries:

```
1 query:  SELECT * FROM users
1 query:  SELECT * FROM posts WHERE user_id IN (1, 2, 3, ...)
1 query:  SELECT * FROM comments WHERE post_id IN (10, 20, 30, ...)
1 query:  SELECT * FROM users WHERE id IN (5, 8, 12, ...)
```

## Basic Setup (Node.js)

```javascript
import DataLoader from 'dataloader';

// Create a loader per-request (not global!)
function createLoaders(db) {
  return {
    userLoader: new DataLoader(async (ids) => {
      const users = await db.users.findAll({
        where: { id: { [Op.in]: ids } }
      });
      // Return in the same order as the input IDs
      const userMap = new Map(users.map(u => [u.id, u]));
      return ids.map(id => userMap.get(id) || null);
    }),

    postsByUserLoader: new DataLoader(async (userIds) => {
      const posts = await db.posts.findAll({
        where: { userId: { [Op.in]: userIds } }
      });
      const postsMap = new Map();
      posts.forEach(post => {
        if (!postsMap.has(post.userId)) postsMap.set(post.userId, []);
        postsMap.get(post.userId).push(post);
      });
      return userIds.map(id => postsMap.get(id) || []);
    }),
  };
}
```

## Per-Request Context

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => ({
    db,
    loaders: createLoaders(db),  // New loaders per request
    user: getUser(req.headers.authorization),
  }),
});
```

## Using in Resolvers

```javascript
const resolvers = {
  Query: {
    user: (_, { id }, { loaders }) => loaders.userLoader.load(id),
    users: (_, __, { loaders }) => loaders.userLoader.loadMany([1, 2, 3]),
  },

  User: {
    // Instead of: (parent) => db.posts.findAll({ where: { userId: parent.id } })
    posts: (user, _, { loaders }) => loaders.postsByUserLoader.load(user.id),
  },

  Post: {
    author: (post, _, { loaders }) => loaders.userLoader.load(post.authorId),
    comments: (post, _, { loaders }) => loaders.commentsByPostLoader.load(post.id),
  },

  Comment: {
    author: (comment, _, { loaders }) => loaders.userLoader.load(comment.authorId),
  },
};
```

## Python (aiodataloader)

```python
from aiodataloader import DataLoader

async def batch_load_users(user_ids):
    users = await db.fetch_all(
        "SELECT * FROM users WHERE id = ANY($1)", user_ids
    )
    user_map = {u["id"]: u for u in users}
    return [user_map.get(uid) for uid in user_ids]

async def batch_load_posts_by_user(user_ids):
    posts = await db.fetch_all(
        "SELECT * FROM posts WHERE user_id = ANY($1)", user_ids
    )
    posts_map = defaultdict(list)
    for post in posts:
        posts_map[post["user_id"]].append(post)
    return [posts_map.get(uid, []) for uid in user_ids]

# In context
class Context:
    def __init__(self):
        self.user_loader = DataLoader(batch_load_users)
        self.posts_loader = DataLoader(batch_load_posts_by_user)
```

## Advanced Patterns

### Caching

DataLoader caches results within a single request by default. For cross-request caching:

```javascript
// Custom cache with Redis
class RedisCacheMap {
  constructor(redis, prefix, ttl = 60) {
    this.redis = redis;
    this.prefix = prefix;
    this.ttl = ttl;
  }

  async get(key) {
    const value = await this.redis.get(`${this.prefix}:${key}`);
    return value ? JSON.parse(value) : undefined;
  }

  async set(key, value) {
    await this.redis.setex(
      `${this.prefix}:${key}`,
      this.ttl,
      JSON.stringify(value)
    );
  }

  async delete(key) {
    await this.redis.del(`${this.prefix}:${key}`);
  }
}

const userLoader = new DataLoader(batchFn, {
  cacheMap: new RedisCacheMap(redis, 'user', 300),
});
```

### Cache Invalidation

```javascript
// After mutation, prime or clear the cache
async function updateUser(id, data, loaders) {
  const updatedUser = await db.users.update(id, data);

  // Option 1: Prime the cache with new data
  loaders.userLoader.clear(id).prime(id, updatedUser);

  // Option 2: Just clear (next load will fetch fresh)
  loaders.userLoader.clear(id);

  return updatedUser;
}
```

### Sorting and Filtering

```javascript
// Key the loader by a compound key
const postsLoader = new DataLoader(async (keys) => {
  // keys = ["user:1:sort:date", "user:2:sort:likes"]
  const userIds = keys.map(k => k.split(':')[1]);
  const posts = await db.posts.findAll({
    where: { userId: { [Op.in]: userIds } },
  });

  const map = new Map();
  posts.forEach(post => {
    const key = `user:${post.userId}:sort:date`;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(post);
  });

  return keys.map(key => map.get(key) || []);
});

// Usage
const userPosts = await postsLoader.load(`user:${userId}:sort:date`);
```

### Error Handling

```javascript
// DataLoader expects the array length to match input IDs
const loader = new DataLoader(async (ids) => {
  try {
    const results = await batchFetch(ids);
    return ids.map(id => results[id] || new Error(`Not found: ${id}`));
  } catch (error) {
    // Return error for ALL items in the batch
    return ids.map(() => error);
  }
});
```

## Batch Function Contract

| Rule | Description |
|------|-------------|
| Array length | Return array must match input array length |
| Order | Return values must correspond to input order |
| Nulls | Use `null` for missing items, not `undefined` |
| Errors | Use Error instances for failed items |

## Performance Tips

1. **Always create loaders per-request** to avoid stale cache leaks
2. **Set `maxBatchSize`** if your database has parameter limits (e.g., 1000 for PostgreSQL)
3. **Use `LOAD_PRIME`** after mutations to keep cache consistent
4. **Monitor batch sizes** - very small batches mean you're not batching effectively
5. **Index foreign keys** - batch queries still need efficient lookups

```javascript
const loader = new DataLoader(batchFn, {
  maxBatchSize: 100,  // Split into batches of 100
  batchScheduleFn: callback => setTimeout(callback, 10),  // 10ms batching window
});
```
