# K8s Manifest Best Practices

## 资源限制

**始终设置 resources**，否则 Pod 可能被 OOMKill 或占用过多节点资源：

```yaml
resources:
  requests:
    cpu: 100m      # 0.1 核
    memory: 128Mi  # 128 MB
  limits:
    cpu: 500m      # 0.5 核
    memory: 512Mi  # 512 MB
```

**经验值**：
- Web API: requests 100m/128Mi, limits 500m/512Mi
- Worker: requests 200m/256Mi, limits 1000m/1Gi
- 数据库: requests 500m/512Mi, limits 2000m/2Gi

## 健康检查

```yaml
livenessProbe:       # 存活：失败则重启容器
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 15

readinessProbe:      # 就绪：失败则从 Service 摘除
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10

startupProbe:        # 启动：慢启动服务用
  httpGet:
    path: /health
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

## 标签规范

```yaml
labels:
  app.kubernetes.io/name: <name>        # 必需
  app.kubernetes.io/version: <version>   # 推荐
  app.kubernetes.io/component: <role>    # 可选
  app.kubernetes.io/part-of: <project>   # 可选
```

## 安全

- 不要用 `latest` 标签，用具体版本
- 设置 `securityContext.runAsNonRoot: true`
- 使用 `readOnlyRootFilesystem: true`
- 不要挂载 ServiceAccount token（除非需要）

## 滚动更新

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # 最多多出 1 个 Pod
    maxUnavailable: 0  # 不允许不可用
```
