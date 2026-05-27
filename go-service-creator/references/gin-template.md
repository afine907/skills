# Gin Framework Template

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

	"github.com/gin-gonic/gin"
)

func main() {
	cfg := config.Load()

	r := setupRouter(cfg)

	srv := &http.Server{
		Addr:         ":" + cfg.Port,
		Handler:      r,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	go func() {
		log.Printf("Server starting on :%s", cfg.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %s", err)
	}
	log.Println("Server exited")
}

func setupRouter(cfg *config.Config) *gin.Engine {
	r := gin.Default()

	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	api := r.Group("/api/v1")
	{
		// Register routes here
		// handler.RegisterUserRoutes(api)
	}

	return r
}
```

## Handler 模式

```go
package handler

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type UserHandler struct {
	// service dependencies
}

func NewUserHandler() *UserHandler {
	return &UserHandler{}
}

func (h *UserHandler) List(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"users": []string{}})
}

func (h *UserHandler) Get(c *gin.Context) {
	id := c.Param("id")
	c.JSON(http.StatusOK, gin.H{"id": id})
}

func (h *UserHandler) Create(c *gin.Context) {
	var req struct {
		Name string `json:"name" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, gin.H{"id": "1", "name": req.Name})
}

func RegisterUserRoutes(rg *gin.RouterGroup) {
	h := NewUserHandler()
	users := rg.Group("/users")
	{
		users.GET("", h.List)
		users.GET("/:id", h.Get)
		users.POST("", h.Create)
	}
}
```

## Middleware 模式

```go
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := c.GetHeader("Authorization")
		if token == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized"})
			return
		}
		// validate token
		c.Next()
	}
}
```
