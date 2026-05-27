# Fiber Framework Template

## main.go

```go
package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"<module>/internal/config"
	"<module>/internal/handler"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/recover"
)

func main() {
	cfg := config.Load()

	app := fiber.New(fiber.Config{
		AppName:      cfg.AppName,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	})

	app.Use(recover.New())
	app.Use(cors.New())

	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{"status": "ok"})
	})

	api := app.Group("/api/v1")
	// handler.RegisterUserRoutes(api)

	// Graceful shutdown
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-quit
		log.Println("Shutting down server...")
		app.Shutdown()
	}()

	log.Printf("Server starting on :%s", cfg.Port)
	log.Fatal(app.Listen(":" + cfg.Port))
}
```

## Handler 模式

```go
package handler

import (
	"github.com/gofiber/fiber/v2"
)

type UserHandler struct{}

func NewUserHandler() *UserHandler {
	return &UserHandler{}
}

func (h *UserHandler) List(c *fiber.Ctx) error {
	return c.JSON(fiber.Map{"users": []string{}})
}

func (h *UserHandler) Get(c *fiber.Ctx) error {
	id := c.Params("id")
	return c.JSON(fiber.Map{"id": id})
}

func (h *UserHandler) Create(c *fiber.Ctx) error {
	type Request struct {
		Name string `json:"name"`
	}
	var req Request
	if err := c.BodyParser(&req); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": err.Error()})
	}
	return c.Status(201).JSON(fiber.Map{"id": "1", "name": req.Name})
}

func RegisterUserRoutes(r fiber.Router) {
	h := NewUserHandler()
	r.Get("/users", h.List)
	r.Get("/users/:id", h.Get)
	r.Post("/users", h.Create)
}
```

## 注意

- Fiber 基于 fasthttp，不是 net/http
- 不兼容标准库 net/http 中间件
- 性能最好，但生态比 Gin 小
