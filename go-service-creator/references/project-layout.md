# Go Project Layout

## 标准目录结构

```
<service>/
├── cmd/
│   └── server/
│       └── main.go           # 程序入口
├── internal/                  # 私有代码（不可被外部 import）
│   ├── config/
│   │   └── config.go         # 配置加载
│   ├── handler/              # HTTP handlers（请求/响应）
│   ├── model/                # 数据模型
│   ├── service/              # 业务逻辑
│   └── repository/           # 数据访问层（可选）
├── pkg/                       # 可被外部 import 的公共代码（可选）
├── api/                       # API 定义（protobuf/OpenAPI，可选）
├── configs/                   # 配置文件模板
├── scripts/                   # 构建/部署脚本
├── go.mod
├── go.sum
├── Makefile
├── Dockerfile
├── .env.example
└── README.md
```

## 目录职责

| 目录 | 职责 | 可被外部 import |
|------|------|----------------|
| `cmd/` | 程序入口，只做组装和启动 | 否 |
| `internal/` | 私有业务代码 | 否（Go 编译器强制） |
| `pkg/` | 可复用的公共库 | 是 |
| `api/` | API 定义文件 | N/A |

## 分层原则

```
handler → service → repository → database
  ↑           ↑
请求解析    业务逻辑    数据访问
```

- **handler**: 只做 HTTP 相关（解析参数、返回响应）
- **service**: 纯业务逻辑，不依赖 HTTP 框架
- **repository**: 数据访问抽象，方便测试时 mock

## 配置管理

使用环境变量 + 默认值，不硬编码：

```go
package config

import "os"

type Config struct {
	Port         string
	DatabaseURL  string
	RedisURL     string
}

func Load() *Config {
	return &Config{
		Port:        getEnv("PORT", "8080"),
		DatabaseURL: getEnv("DATABASE_URL", ""),
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
```
