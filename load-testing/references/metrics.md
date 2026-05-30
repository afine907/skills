# Load Testing Metrics Reference

## Core HTTP Metrics

### Response Time (Latency)

| Metric | Description | Good Target |
|--------|-------------|-------------|
| `http_req_duration` | Total time from request start to response end | - |
| `http_req_waiting` | Time spent waiting for server response (TTFB) | < 200ms |
| `http_req_connecting` | TCP connection time | < 100ms |
| `http_req_tls_handshaking` | TLS handshake time | < 150ms |
| `http_req_sending` | Time sending request body | < 50ms |
| `http_req_receiving` | Time receiving response body | < 100ms |

### Percentiles

| Percentile | Meaning | Why It Matters |
|------------|---------|----------------|
| p50 (median) | 50% of requests are faster | Typical user experience |
| p90 | 90% of requests are faster | Most users' experience |
| p95 | 95% of requests are faster | Good SLA target |
| p99 | 99% of requests are faster | Tail latency, catches outliers |
| p99.9 | 99.9% of requests are faster | Extreme edge cases |

**Target**: p95 < 500ms for APIs, p95 < 2s for page loads.

### Throughput

```
Requests per second (RPS) = Total requests / Duration

Target: Depends on your infrastructure capacity
Example: 1000 RPS for a typical web API
```

### Error Rate

```
Error Rate = Failed Requests / Total Requests * 100%

Target: < 1% for production-like load
Acceptable: < 5% during peak stress
```

## System Metrics

### CPU

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| CPU Utilization | < 60% | 60-80% | > 80% |
| Load Average (per core) | < 1.0 | 1.0-2.0 | > 2.0 |

### Memory

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Memory Usage | < 70% | 70-85% | > 85% |
| Swap Usage | 0% | Any usage | > 10% |

### Disk I/O

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Disk Utilization | < 70% | 70-85% | > 85% |
| I/O Wait | < 5% | 5-15% | > 15% |

### Network

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Bandwidth Utilization | < 50% | 50-70% | > 70% |
| Packet Loss | 0% | < 0.1% | > 0.1% |
| TCP Retransmits | < 0.5% | 0.5-2% | > 2% |

## Application Metrics

### Database

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Query latency (p95) | < 50ms | > 200ms |
| Connection pool usage | < 70% | > 85% |
| Active connections | < 80% of max | > 90% |
| Slow queries (> 1s) | < 1/min | > 5/min |
| Deadlocks | 0 | > 0 |

### Cache (Redis)

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Hit rate | > 90% | < 80% |
| Latency (p95) | < 1ms | > 5ms |
| Memory usage | < 70% | > 85% |
| Evictions | 0/min | > 10/min |
| Connected clients | < 70% of max | > 85% |

### Message Queue

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Queue depth | < 1000 | > 10000 |
| Consumer lag | < 10s | > 60s |
| Publish rate | Within capacity | > 80% capacity |
| Error rate | < 0.1% | > 1% |

## Load Test Profiles

### Smoke Test

```
VUs: 1-5
Duration: 1-2 minutes
Purpose: Verify the system works under minimal load
```

### Load Test

```
VUs: Expected concurrent users
Duration: 15-30 minutes
Purpose: Verify performance under expected load
```

### Stress Test

```
VUs: 2-5x expected load
Duration: 15-30 minutes
Purpose: Find the breaking point
```

### Soak Test

```
VUs: Expected load
Duration: 4-24 hours
Purpose: Detect memory leaks, connection leaks, degradation
```

### Spike Test

```
VUs: 10x expected load (sudden)
Duration: 5-15 minutes
Purpose: Verify recovery after traffic spike
```

## Interpreting Results

### Key Indicators

```
Good result:
  - Response times stable throughout test
  - Error rate < 1%
  - Throughput scales linearly with VUs
  - System metrics within healthy range

Bad result:
  - Response times increase over time (degradation)
  - Error rate spikes at certain VU count (breaking point)
  - Throughput plateaus (bottleneck)
  - Memory usage grows continuously (leak)
```

### Finding Bottlenecks

```
High CPU → Check inefficient algorithms, N+1 queries
High Memory → Check for leaks, large object caching
High Disk I/O → Check logging volume, temp files
High Network → Check payload sizes, missing compression
High DB connections → Check connection pool, slow queries
Low throughput despite resources → Check thread pool, connection limits
```

## SLA Definitions

```yaml
availability:
  target: 99.9%  # 8.76 hours downtime/year

latency:
  p50: 200ms
  p95: 500ms
  p99: 1000ms

throughput:
  sustained: 1000 rps
  peak: 5000 rps

error_rate:
  target: < 0.1%
  max: < 1%
```
