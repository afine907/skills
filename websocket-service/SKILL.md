---
name: websocket-service
description: |
  【WebSocket服务】设计和实现 WebSocket 实时通信服务。触发时机：用户说"WebSocket"、"实时通信"、"长连接"、"消息推送"时。
category: development
---

# WebSocket Service — WebSocket 实时通信服务

设计和实现可靠的 WebSocket 实时通信系统。


## Goal

设计和实现 WebSocket 实时通信服务，包含连接管理、消息协议、心跳检测、断线重连、房间/频道管理

## Trigger

- 用户要求"实时通信"、"WebSocket"、"推送服务"
  - 需要实现聊天、通知、实时数据更新
  - 需要服务器主动推送

## 技术选型

| 框架 | 语言 | 特点 | 适用场景 |
|------|------|------|----------|
| Socket.IO | Node.js/Python | 自动降级、房间、命名空间 | 通用实时应用 |
| ws | Node.js | 轻量、原生 | 高性能场景 |
| FastAPI WebSocket | Python | 原生支持、类型安全 | Python 后端 |
| Centrifugo | 独立服务 | 高性能、多语言 SDK | 大规模推送 |

## 消息协议设计

### 消息格式

```json
{
  "type": "message",
  "id": "msg_123",
  "timestamp": 1704067200000,
  "from": "user_456",
  "to": "user_789",
  "payload": {
    "content": "Hello",
    "contentType": "text"
  }
}
```

### 消息类型

| 类型 | 方向 | 说明 |
|------|------|------|
| `auth` | C→S | 认证消息 |
| `auth_ok` | S→C | 认证成功 |
| `message` | C↔S | 聊天消息 |
| `typing` | C→S | 正在输入 |
| `presence` | S→C | 在线状态 |
| `join` | C→S | 加入房间 |
| `leave` | C→S | 离开房间 |
| `error` | S→C | 错误消息 |
| `ping/pong` | C↔S | 心跳 |

## Python + FastAPI 实现

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        # 用户连接映射
        self.active_connections: Dict[str, WebSocket] = {}
        # 房间映射
        self.rooms: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
    
    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        # 从所有房间移除
        for room in self.rooms.values():
            room.discard(user_id)
    
    async def send_personal(self, user_id: str, message: dict):
        ws = self.active_connections.get(user_id)
        if ws:
            await ws.send_json(message)
    
    async def broadcast(self, message: dict, exclude: str = None):
        for user_id, ws in self.active_connections.items():
            if user_id != exclude:
                await ws.send_json(message)
    
    def join_room(self, user_id: str, room: str):
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(user_id)
    
    def leave_room(self, user_id: str, room: str):
        if room in self.rooms:
            self.rooms[room].discard(user_id)
    
    async def broadcast_to_room(self, room: str, message: dict, exclude: str = None):
        for user_id in self.rooms.get(room, set()):
            if user_id != exclude:
                await self.send_personal(user_id, message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    # 通知上线
    await manager.broadcast({
        "type": "presence",
        "user_id": user_id,
        "status": "online"
    }, exclude=user_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            await handle_message(user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        # 通知下线
        await manager.broadcast({
            "type": "presence",
            "user_id": user_id,
            "status": "offline"
        })

async def handle_message(sender_id: str, data: dict):
    msg_type = data.get("type")
    
    if msg_type == "message":
        # 私聊消息
        to = data.get("to")
        await manager.send_personal(to, {
            "type": "message",
            "from": sender_id,
            "payload": data.get("payload")
        })
    
    elif msg_type == "join":
        room = data.get("room")
        manager.join_room(sender_id, room)
        await manager.broadcast_to_room(room, {
            "type": "join",
            "user_id": sender_id,
            "room": room
        })
    
    elif msg_type == "leave":
        room = data.get("room")
        manager.leave_room(sender_id, room)
        await manager.broadcast_to_room(room, {
            "type": "leave",
            "user_id": sender_id,
            "room": room
        })
    
    elif msg_type == "room_message":
        room = data.get("room")
        await manager.broadcast_to_room(room, {
            "type": "message",
            "from": sender_id,
            "room": room,
            "payload": data.get("payload")
        }, exclude=sender_id)
    
    elif msg_type == "ping":
        await manager.send_personal(sender_id, {"type": "pong"})
```

## Node.js + Socket.IO 实现

```javascript
const { Server } = require('socket.io');
const jwt = require('jsonwebtoken');

const io = new Server(3000, {
  cors: { origin: '*' }
});

// 认证中间件
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    socket.userId = decoded.userId;
    next();
  } catch (err) {
    next(new Error('Authentication error'));
  }
});

io.on('connection', (socket) => {
  console.log(`User connected: ${socket.userId}`);
  
  // 加入个人房间
  socket.join(`user:${socket.userId}`);
  
  // 通知上线
  socket.broadcast.emit('presence', {
    userId: socket.userId,
    status: 'online'
  });
  
  // 私聊消息
  socket.on('message', async (data) => {
    const { to, payload } = data;
    io.to(`user:${to}`).emit('message', {
      from: socket.userId,
      payload,
      timestamp: Date.now()
    });
  });
  
  // 加入房间
  socket.on('join', (room) => {
    socket.join(room);
    io.to(room).emit('join', {
      userId: socket.userId,
      room
    });
  });
  
  // 离开房间
  socket.on('leave', (room) => {
    socket.leave(room);
    io.to(room).emit('leave', {
      userId: socket.userId,
      room
    });
  });
  
  // 房间消息
  socket.on('room_message', (data) => {
    const { room, payload } = data;
    socket.to(room).emit('message', {
      from: socket.userId,
      room,
      payload,
      timestamp: Date.now()
    });
  });
  
  // 断开连接
  socket.on('disconnect', () => {
    socket.broadcast.emit('presence', {
      userId: socket.userId,
      status: 'offline'
    });
  });
});
```

## 客户端实现

```typescript
// React Hook
import { useEffect, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

export function useSocket(userId: string, token: string) {
  const socketRef = useRef<Socket | null>(null);
  
  useEffect(() => {
    socketRef.current = io('http://localhost:3000', {
      auth: { token }
    });
    
    socketRef.current.on('connect', () => {
      console.log('Connected');
    });
    
    socketRef.current.on('disconnect', () => {
      console.log('Disconnected');
    });
    
    return () => {
      socketRef.current?.disconnect();
    };
  }, [userId, token]);
  
  const sendMessage = useCallback((to: string, content: string) => {
    socketRef.current?.emit('message', {
      to,
      payload: { content, contentType: 'text' }
    });
  }, []);
  
  const joinRoom = useCallback((room: string) => {
    socketRef.current?.emit('join', room);
  }, []);
  
  const sendRoomMessage = useCallback((room: string, content: string) => {
    socketRef.current?.emit('room_message', {
      room,
      payload: { content, contentType: 'text' }
    });
  }, []);
  
  return { sendMessage, joinRoom, sendRoomMessage, socket: socketRef.current };
}
```

## 心跳检测

```python
# 服务端心跳
async def heartbeat_checker():
    while True:
        await asyncio.sleep(30)
        for user_id, ws in manager.active_connections.items():
            try:
                await ws.send_json({"type": "ping"})
            except:
                manager.disconnect(user_id)
```

```javascript
// 客户端心跳
socket.on('pong', () => {
  lastPong = Date.now();
});

setInterval(() => {
  if (Date.now() - lastPong > 35000) {
    socket.disconnect();
    socket.connect();
  }
  socket.emit('ping');
}, 30000);
```

## 快速使用

```
# 设计 WebSocket 服务
设计一个聊天室的 WebSocket 服务

# 实现实时推送
实现服务器主动推送通知

# 添加房间功能
实现多人聊天室的房间管理

# 处理断线重连
实现客户端断线自动重连
```

## 参考资料

- Socket.IO 文档: [references/socketio.md](references/socketio.md)
- WebSocket 协议: [references/websocket-protocol.md](references/websocket-protocol.md)
