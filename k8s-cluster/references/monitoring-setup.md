# Monitoring Setup

## Metrics Server 安装

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 验证
kubectl top nodes
kubectl top pods
```

## Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: <service-name>
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: <service-name>
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

## 告警规则

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: <service-name>-alerts
spec:
  groups:
    - name: <service-name>
      rules:
        - alert: HighErrorRate
          expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "High error rate on {{ $labels.instance }}"

        - alert: HighLatency
          expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1
          for: 5m
          labels:
            severity: warning
          annotations:
            summary: "High latency on {{ $labels.instance }}"
```

## 资源配额

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: <namespace>-quota
  namespace: <namespace>
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "20"
```

## LimitRange（默认限制）

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: <namespace>-limits
  namespace: <namespace>
spec:
  limits:
    - default:
        cpu: 500m
        memory: 512Mi
      defaultRequest:
        cpu: 100m
        memory: 128Mi
      type: Container
```
