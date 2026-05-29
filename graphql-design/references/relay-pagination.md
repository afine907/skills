# Relay-Style Pagination

## Overview

Relay pagination uses cursor-based pagination with a standardized connection model. It is the recommended approach for GraphQL APIs that need stable, efficient pagination.

## Schema Definition

```graphql
type Query {
  users(
    first: Int
    after: String
    last: Int
    before: String
    filter: UserFilter
  ): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

## Query Examples

### Forward Pagination (Next Page)

```graphql
query {
  users(first: 10, after: "cursor-abc") {
    edges {
      node {
        id
        name
        email
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}
```

### Backward Pagination (Previous Page)

```graphql
query {
  users(last: 10, before: "cursor-xyz") {
    edges {
      node {
        id
        name
      }
      cursor
    }
    pageInfo {
      hasPreviousPage
      startCursor
    }
  }
}
```

## Server Implementation (Node.js)

```javascript
const resolvers = {
  Query: {
    users: async (_, { first, after, last, before, filter }, context) => {
      const limit = first || last;
      const cursor = after || before;

      // Decode cursor to get position
      const cursorOffset = cursor ? decodeCursor(cursor) : 0;

      // Fetch one extra to determine hasNextPage/hasPreviousPage
      const fetchLimit = limit + 1;

      const users = await context.db.users.findAll({
        where: buildFilter(filter),
        limit: fetchLimit,
        offset: after ? cursorOffset + 1 : cursorOffset,
        order: after ? 'ASC' : 'DESC',
      });

      const hasMore = users.length > limit;
      const slicedUsers = users.slice(0, limit);

      // If backward pagination, reverse to maintain order
      if (before) slicedUsers.reverse();

      return {
        edges: slicedUsers.map(user => ({
          node: user,
          cursor: encodeCursor(user.id),
        })),
        pageInfo: {
          hasNextPage: after ? hasMore : false,
          hasPreviousPage: before ? hasMore : false,
          startCursor: slicedUsers[0] ? encodeCursor(slicedUsers[0].id) : null,
          endCursor: slicedUsers.length > 0
            ? encodeCursor(slicedUsers[slicedUsers.length - 1].id)
            : null,
        },
        totalCount: await context.db.users.count({ where: buildFilter(filter) }),
      };
    },
  },
};
```

## Cursor Encoding

```javascript
// Use opaque cursors (base64-encoded)
function encodeCursor(id) {
  return Buffer.from(`cursor:${id}`).toString('base64');
}

function decodeCursor(cursor) {
  const decoded = Buffer.from(cursor, 'base64').toString('utf-8');
  return decoded.replace('cursor:', '');
}
```

## Client-Side (React + Apollo)

```tsx
import { useQuery, gql } from '@apollo/client';

const GET_USERS = gql`
  query GetUsers($first: Int!, $after: String) {
    users(first: $first, after: $after) {
      edges {
        node { id name email }
        cursor
      }
      pageInfo {
        hasNextPage
        endCursor
      }
    }
  }
`;

function UserList() {
  const { data, loading, fetchMore } = useQuery(GET_USERS, {
    variables: { first: 20 },
  });

  const loadMore = () => {
    fetchMore({
      variables: {
        after: data.users.pageInfo.endCursor,
      },
    });
  };

  return (
    <div>
      {data?.users.edges.map(({ node }) => (
        <div key={node.id}>{node.name}</div>
      ))}
      {data?.users.pageInfo.hasNextPage && (
        <button onClick={loadMore}>Load More</button>
      )}
    </div>
  );
}
```

## Relay Client

```tsx
import { useLazyLoadQuery, usePaginationFragment, graphql } from 'react-relay';

const UsersListFragment = graphql`
  fragment UsersList_query on Query
  @refetchable(queryName: "UsersListPaginationQuery") {
    users(first: $count, after: $cursor)
      @connection(key: "UsersList_users") {
      edges {
        node {
          id
          name
        }
      }
    }
  }
`;

function UsersList({ queryRef }) {
  const { data, loadNext, isLoadingNext, hasNext } = usePaginationFragment(
    UsersListFragment,
    queryRef
  );

  return (
    <>
      {data.users.edges.map(({ node }) => (
        <div key={node.id}>{node.name}</div>
      ))}
      {hasNext && (
        <button onClick={() => loadNext(20)} disabled={isLoadingNext}>
          {isLoadingNext ? 'Loading...' : 'Load More'}
        </button>
      )}
    </>
  );
}
```

## Offset vs Cursor Pagination

| Aspect | Offset-Based | Cursor-Based (Relay) |
|--------|-------------|---------------------|
| URL | `?page=5` | `?after=abc123` |
| Consistency | Items shift on insert/delete | Stable results |
| Deep pagination | Slow (OFFSET N) | Fast (WHERE id > cursor) |
| Total count | Easy | Requires separate query |
| Random access | Yes (jump to page 50) | No (sequential only) |

## Best Practices

1. **Always use opaque cursors** - Don't expose internal IDs or offsets
2. **Cap page size** - Enforce maximum `first`/`last` (e.g., 100)
3. **Index cursor columns** - Ensure the cursor column is indexed
4. **Handle empty pages** - Return empty edges array, not null
5. **Consider totalCount cost** - It can be expensive on large tables; make it optional
6. **Use `@connection` directive** in Relay for automatic cache normalization
