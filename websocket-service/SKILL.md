---
name: websocket-service
description: |
  【WebSocket服务】设计和实现 WebSocket 实时通信服务。

  触发时机：
  - 用户要求"WebSocket"、"实时通信"、"长连接"、"消息推送"
category: development
---

# WebSocket Service — 实时通信服务

设计和实现可靠的 WebSocket 实时通信系统。

## Workflow

1. **需求分析** — 通信模式 (点对点/广播/房间)、消息格式
2. **选择方案** — Socket.IO / ws / 原生 WebSocket
3. **设计协议** — 消息类型、心跳、重连
4. **实现服务** — 连接管理、消息路由、房间管理
5. **部署运维** — 负载均衡、水平扩展、监控

## 核心实现

### Socket.IO Server (Node.js)

```javascript
const { Server } = require('socket.io');
const io = new Server(httpServer, {
  cors: { origin: '*' },
  pingTimeout: 60000,
  pingInterval: 25000,
});

// 房间管理
io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  // 加入房间
  socket.on('join:room', (roomId) => {
    socket.join(roomId);
    socket.to(roomId).emit('user:joined', { userId: socket.id });
  });

  // 房间消息
  socket.on('message:room', ({ roomId, message }) => {
    io.to(roomId).emit('message:new', {
      userId: socket.id,
      message,
      timestamp: Date.now(),
    });
  });

  // 私聊
  socket.on('message:private', ({ targetId, message }) => {
    socket.to(targetId).emit('message:private', {
      from: socket.id,
      message,
    });
  });

  socket.on('disconnect', () => {
    console.log(`User disconnected: ${socket.id}`);
  });
});
```

### Python FastAPI WebSocket

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set

app = FastAPI()
rooms: Dict[str, Set[WebSocket]] = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = set()
    rooms[room_id].add(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            # 广播给房间内其他人
            for ws in rooms[room_id]:
                if ws != websocket:
                    await ws.send_json(data)
    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
```

## 消息协议

```json
{
  "type": "chat | system | ack | error",
  "payload": {},
  "timestamp": 1704067200000,
  "id": "uuid"
}
```

## Example

```
用户: 实现一个多人聊天室

输出:
1. Socket.IO server，支持房间管理
2. 客户端: join:room, message:room 事件
3. 心跳检测: ping/pong 25s 间隔
4. 断线重连: 指数退避，最多 5 次
5. 消息持久化: Redis pub/sub 跨实例广播
```

## 参考

- Socket.IO: [references/socketio.md](references/socketio.md)
- WebSocket 协议: [references/websocket-protocol.md](references/websocket-protocol.md)
