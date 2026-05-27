# Echo Framework Template

## main.go

```go
package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"<module>/internal/config"
	"<module>/internal/handler"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	cfg := config.Load()

	e := echo.New()
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Use(middleware.CORS())

	e.GET("/health", func(c echo.Context) error {
		return c.JSON(200, map[string]string{"status": "ok"})
	})

	api := e.Group("/api/v1")
	// handler.RegisterUserRoutes(api)

	go func() {
		log.Printf("Server starting on :%s", cfg.Port)
		if err := e.Start(":" + cfg.Port); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := e.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %s", err)
	}
	log.Println("Server exited")
}
```

## Handler 模式

```go
package handler

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

type UserHandler struct{}

func NewUserHandler() *UserHandler {
	return &UserHandler{}
}

func (h *UserHandler) List(c echo.Context) error {
	return c.JSON(http.StatusOK, map[string]interface{}{"users": []string{}})
}

func (h *UserHandler) Get(c echo.Context) error {
	id := c.Param("id")
	return c.JSON(http.StatusOK, map[string]interface{}{"id": id})
}

func (h *UserHandler) Create(c echo.Context) error {
	var req struct {
		Name string `json:"name" validate:"required"`
	}
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}
	return c.JSON(http.StatusCreated, map[string]interface{}{"id": "1", "name": req.Name})
}

func RegisterUserRoutes(g *echo.Group) {
	h := NewUserHandler()
	g.GET("/users", h.List)
	g.GET("/users/:id", h.Get)
	g.POST("/users", h.Create)
}
```
