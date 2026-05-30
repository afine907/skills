# Socket.IO 参考文档

## 概述

Socket.IO 是一个实时双向通信库，基于 WebSocket 协议，支持自动降级、房间、命名空间等高级功能。

## 服务端 (Node.js)

### 安装

```bash
npm install socket.io
```

### 基础服务器

```javascript
const { Server } = require('socket.io');

const io = new Server(3000, {
  cors: {
    origin: "http://localhost:3001",
    methods: ["GET", "POST"]
  }
});

io.on('connection', (socket) => {
  console.log('User connected:', socket.id);
  
  // 监听事件
  socket.on('message', (data) => {
    console.log('Message:', data);
    // 广播给所有客户端
    io.emit('message', data);
  });
  
  // 断开连接
  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});
```

### 房间管理

```javascript
io.on('connection', (socket) => {
  // 加入房间
  socket.on('join', (room) => {
    socket.join(room);
    io.to(room).emit('user_joined', socket.id);
  });
  
  // 离开房间
  socket.on('leave', (room) => {
    socket.leave(room);
    io.to(room).emit('user_left', socket.id);
  });
  
  // 发送到房间
  socket.on('room_message', (room, message) => {
    io.to(room).emit('message', {
      from: socket.id,
      content: message
    });
  });
  
  // 私聊
  socket.on('private_message', (to, message) => {
    io.to(to).emit('private_message', {
      from: socket.id,
      content: message
    });
  });
});
```

### 命名空间

```javascript
// 聊天命名空间
const chatNsp = io.of('/chat');
chatNsp.on('connection', (socket) => {
  socket.on('message', (data) => {
    chatNsp.emit('message', data);
  });
});

// 通知命名空间
const notifyNsp = io.of('/notify');
notifyNsp.on('connection', (socket) => {
  socket.on('subscribe', (userId) => {
    socket.join(`user:${userId}`);
  });
});
```

### 中间件

```javascript
// 认证中间件
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  if (!token) {
    return next(new Error('Authentication error'));
  }
  
  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    socket.userId = decoded.userId;
    next();
  } catch (err) {
    next(new Error('Invalid token'));
  }
});

// 日志中间件
io.use((socket, next) => {
  console.log(`[${new Date().toISOString()}] ${socket.id} connecting`);
  next();
});
```

## 客户端 (JavaScript)

### 安装

```bash
npm install socket.io-client
```

### 基础连接

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:3000', {
  auth: {
    token: 'your-jwt-token'
  }
});

// 连接成功
socket.on('connect', () => {
  console.log('Connected:', socket.id);
});

// 监听消息
socket.on('message', (data) => {
  console.log('Message:', data);
});

// 发送消息
socket.emit('message', { content: 'Hello' });

// 断开连接
socket.on('disconnect', () => {
  console.log('Disconnected');
});
```

### React Hook

```typescript
import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

export function useSocket(url: string, token: string) {
  const socketRef = useRef<Socket | null>(null);
  
  useEffect(() => {
    socketRef.current = io(url, {
      auth: { token }
    });
    
    return () => {
      socketRef.current?.disconnect();
    };
  }, [url, token]);
  
  const emit = useCallback((event: string, data?: any) => {
    socketRef.current?.emit(event, data);
  }, []);
  
  const on = useCallback((event: string, callback: (...args: any[]) => void) => {
    socketRef.current?.on(event, callback);
    return () => {
      socketRef.current?.off(event, callback);
    };
  }, []);
  
  return { emit, on, socket: socketRef.current };
}
```

## 高级功能

### 二进制数据

```javascript
// 发送二进制数据
socket.emit('upload', buffer);

// 接收二进制数据
socket.on('file', (data) => {
  const blob = new Blob([data]);
});
```

### 确认回调

```javascript
// 服务端
socket.on('create_post', (data, callback) => {
  const post = createPost(data);
  callback({ status: 'ok', post });
});

// 客户端
socket.emit('create_post', postData, (response) => {
  console.log(response.status);
  console.log(response.post);
});
```

### 连接状态管理

```javascript
socket.on('connect_error', (error) => {
  console.log('Connection error:', error.message);
});

socket.on('reconnect', (attemptNumber) => {
  console.log('Reconnected after', attemptNumber, 'attempts');
});

socket.on('reconnect_attempt', () => {
  console.log('Attempting to reconnect...');
});

socket.on('reconnect_error', (error) => {
  console.log('Reconnection error:', error.message);
});

socket.on('reconnect_failed', () => {
  console.log('Failed to reconnect');
});
```

## 性能优化

### 消息压缩

```javascript
const io = new Server(3000, {
  perMessageDeflate: {
    threshold: 1024  // 只压缩大于 1KB 的消息
  }
});
```

### 连接限制

```javascript
const io = new Server(3000, {
  maxHttpBufferSize: 1e6,  // 1MB
  pingTimeout: 60000,
  pingInterval: 25000
});
```

## 错误处理

```javascript
socket.on('connect_error', (err) => {
  if (err.message === 'Authentication error') {
    // 重新登录
    refreshToken().then(newToken => {
      socket.auth.token = newToken;
      socket.connect();
    });
  }
});
```

## 官方文档

- https://socket.io/docs/v4/
