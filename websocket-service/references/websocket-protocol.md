# WebSocket 协议参考

## 概述

WebSocket 是一种在单个 TCP 连接上进行全双工通信的协议，专为 Web 应用设计，提供低延迟的双向数据传输。

## 协议特点

| 特点 | 说明 |
|------|------|
| 全双工 | 客户端和服务器可同时发送数据 |
| 低延迟 | 无需频繁建立连接 |
| 轻量头 | 仅 2-14 字节开销（vs HTTP 数百字节） |
| 持久连接 | 一次握手，持续通信 |
| 二进制支持 | 支持文本和二进制数据 |

## 握手过程

### 客户端请求

```http
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: http://example.com
```

### 服务器响应

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

## 帧格式

```
 0               1               2               3
 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7 0 1 2 3 4 5 6 7
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+-------------------------------+
|     Extended payload length continued, if payload len == 127  |
+-------------------------------+-------------------------------+
|                               |Masking-key, if MASK set to 1  |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------+-------------------------------+
```

## 操作码

| 操作码 | 含义 | 说明 |
|--------|------|------|
| 0x0 | Continuation | 帧的延续 |
| 0x1 | Text | 文本帧 |
| 0x2 | Binary | 二进制帧 |
| 0x8 | Close | 关闭连接 |
| 0x9 | Ping | 心跳请求 |
| 0xA | Pong | 心跳响应 |

## 状态码

| 状态码 | 含义 |
|--------|------|
| 1000 | 正常关闭 |
| 1001 | 端点离开（如页面关闭） |
| 1002 | 协议错误 |
| 1003 | 不支持的数据类型 |
| 1006 | 异常关闭（无状态码） |
| 1007 | 数据格式错误 |
| 1008 | 策略违规 |
| 1009 | 消息过大 |
| 1010 | 缺少扩展 |
| 1011 | 服务器错误 |
| 1015 | TLS 握手失败 |

## JavaScript API

### 创建连接

```javascript
const ws = new WebSocket('ws://localhost:8080');

// 或使用安全连接
const wss = new WebSocket('wss://example.com');
```

### 事件处理

```javascript
// 连接打开
ws.onopen = (event) => {
  console.log('Connected');
  ws.send('Hello Server!');
};

// 接收消息
ws.onmessage = (event) => {
  console.log('Message:', event.data);
};

// 连接关闭
ws.onclose = (event) => {
  console.log('Closed:', event.code, event.reason);
};

// 错误处理
ws.onerror = (error) => {
  console.error('Error:', error);
};
```

### 发送数据

```javascript
// 发送文本
ws.send('Hello');

// 发送 JSON
ws.send(JSON.stringify({ type: 'message', content: 'Hello' }));

// 发送二进制
const buffer = new ArrayBuffer(16);
ws.send(buffer);

// 发送 Blob
const blob = new Blob(['Hello'], { type: 'text/plain' });
ws.send(blob);
```

### 关闭连接

```javascript
// 正常关闭
ws.close(1000, 'Normal closure');

// 强制关闭
ws.close();
```

## 服务端实现 (Node.js)

### 原生 ws 库

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // 接收消息
  ws.on('message', (message) => {
    console.log('Received:', message.toString());
    
    // 广播给所有客户端
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message.toString());
      }
    });
  });
  
  // 关闭
  ws.on('close', () => {
    console.log('Client disconnected');
  });
  
  // 发送消息
  ws.send('Welcome!');
});
```

### 心跳检测

```javascript
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  ws.isAlive = true;
  
  ws.on('pong', () => {
    ws.isAlive = true;
  });
});

// 定期检查
const interval = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (ws.isAlive === false) {
      return ws.terminate();
    }
    
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

wss.on('close', () => {
  clearInterval(interval);
});
```

## Python 实现

### websockets 库

```python
import asyncio
import websockets

async def handler(websocket, path):
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(f"Echo: {message}")

start_server = websockets.serve(handler, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

### FastAPI WebSocket

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

## 安全考虑

### 使用 wss://

```javascript
// 生产环境必须使用 wss://
const ws = new WebSocket('wss://example.com');
```

### 验证来源

```javascript
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws, req) => {
  const origin = req.headers.origin;
  if (!isValidOrigin(origin)) {
    ws.close(1008, 'Invalid origin');
    return;
  }
});
```

### 限制消息大小

```javascript
const wss = new WebSocket.Server({
  port: 8080,
  maxPayload: 1024 * 1024  // 1MB
});
```

## 性能优化

### 消息压缩

```javascript
const WebSocket = require('ws');

const wss = new WebSocket.Server({
  port: 8080,
  perMessageDeflate: {
    zlibDeflateOptions: {
      level: 6
    },
    threshold: 1024
  }
});
```

### 连接池

```javascript
class WebSocketPool {
  constructor(maxConnections) {
    this.maxConnections = maxConnections;
    this.connections = new Set();
  }
  
  add(ws) {
    if (this.connections.size >= this.maxConnections) {
      // 关闭最旧的连接
      const oldest = this.connections.values().next().value;
      oldest.close(1001, 'Connection limit reached');
      this.connections.delete(oldest);
    }
    this.connections.add(ws);
  }
  
  remove(ws) {
    this.connections.delete(ws);
  }
  
  broadcast(message) {
    this.connections.forEach(ws => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(message);
      }
    });
  }
}
```

## 官方文档

- RFC 6455: https://tools.ietf.org/html/rfc6455
- MDN: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
