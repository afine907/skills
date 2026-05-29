---
name: k8s-cluster
category: operations
description: |
  Kubernetes 集群管理配置生成器。自然语言描述 → 集群配置/Helm chart/RBAC/扩缩/监控配置。
---

# K8s Cluster — Kubernetes 集群管理配置生成

自然语言描述 → 集群配置文件/脚本/Helm chart，一次输出。

不适用：单个服务的 K8s 部署配置（用 k8s-gen）；Docker 容器配置（用 docker-essentials）。


## Goal

Kubernetes 集群管理配置生成器。自然语言描述 → 集群配置/Helm chart/RBAC/扩缩/监控配置

## Trigger

当用户需要使用此技能时触发。

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
描述需求 → 识别场景 → 生成配置 → 验证
```

### Step 1: 识别场景

| 用户描述 | 场景 | 产出物 |
|----------|------|--------|
| "搭建集群"、"初始化 k8s" | 集群搭建 | setup 脚本 / kind 配置 |
| "写 Helm chart"、"打包成 Helm" | Helm chart | Chart.yaml + values.yaml + templates/ |
| "设置权限"、"RBAC" | 权限配置 | Role/RoleBinding YAML |
| "自动扩缩"、"HPA" | 扩缩配置 | HPA + PDB YAML |
| "监控"、"Prometheus" | 监控配置 | ServiceMonitor + 告警规则 |

可以同时生成多个场景的配置。

### Step 2: 生成配置

按场景读取对应模板：

**集群搭建** → [references/setup-scripts.md](references/setup-scripts.md)
- kubeadm 脚本
- kind 多节点配置
- 托管 K8s（EKS/GKE/AKS）命令

**Helm chart** → [references/helm-chart-template.md](references/helm-chart-template.md)
- Chart.yaml
- values.yaml
- templates/deployment.yaml
- templates/service.yaml
- templates/ingress.yaml
- templates/_helpers.tpl

**RBAC** → [references/rbac-patterns.md](references/rbac-patterns.md)
- Role + RoleBinding
- ClusterRole + ClusterRoleBinding
- ServiceAccount

**扩缩** → [references/scaling-patterns.md](references/scaling-patterns.md)
- HPA（CPU/内存/自定义指标）
- PDB（PodDisruptionBudget）

**监控** → [references/monitoring-setup.md](references/monitoring-setup.md)
- Prometheus ServiceMonitor
- 告警规则
- Grafana dashboard 配置

### Step 3: 验证

Helm chart:
```bash
helm template <chart-name> <chart-dir>
```

YAML manifests:
```bash
kubectl apply --dry-run=client -f <dir>/
```

## 输出格式

```markdown
## K8s 集群配置已生成

**场景**: <搭建/Helm/RBAC/扩缩/监控>

### 生成的文件
- <file1> — <说明>
- ...

### 使用方式
```bash
<next steps>
```
```
