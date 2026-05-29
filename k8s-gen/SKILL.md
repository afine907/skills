---
name: k8s-gen
category: operations
description: |
  Kubernetes 部署配置生成器。自然语言描述 → YAML manifests（Deployment/Service/Ingress/ConfigMap）。
---

# K8s Gen — Kubernetes 部署配置生成

自然语言描述 → 完整 K8s YAML manifests，一次输出。

不适用：集群搭建（用 k8s-cluster）；Helm chart 开发（用 k8s-cluster）。


## Goal

Kubernetes 部署配置生成器。自然语言描述 → YAML manifests（Deployment/Service/Ingress/ConfigMap）

## Trigger

当用户需要使用此技能时触发。

## Workflow

```
输入 → 处理 → 输出
```
## 工作流程

```
描述服务 → 收集配置 → 生成 YAML → 验证
```

### Step 1: 收集服务信息

从用户描述中提取：
- **服务名称**：用于 metadata.name 和 labels
- **镜像名**：container image
- **端口**：容器端口和服务端口
- **副本数**：默认 2
- **环境变量**：从描述或 .env 文件提取
- **是否需要 Ingress**：有域名则需要
- **资源限制**：CPU/Memory（有默认值）

如果用户提供了 Dockerfile 或已有项目，从中推断配置。

### Step 2: 生成 YAML 文件

生成到用户指定目录或当前目录下的 `k8s/` 子目录：

| 文件 | 必需 | 说明 |
|------|------|------|
| `deployment.yaml` | ✅ | Deployment + 资源限制 + 健康检查 |
| `service.yaml` | ✅ | Service |
| `ingress.yaml` | 有域名时 | Ingress + TLS |
| `configmap.yaml` | 有配置时 | 环境变量配置 |
| `secret.yaml` | 有敏感信息时 | Secret 模板 |
| `namespace.yaml` | 可选 | 命名空间 |
| `kustomization.yaml` | 可选 | Kustomize 配置 |

模板参考：
- Deployment/Service → [references/deployment-templates.md](references/deployment-templates.md)
- ConfigMap/Secret → [references/config-templates.md](references/config-templates.md)
- Ingress → [references/ingress-templates.md](references/ingress-templates.md)

### Step 3: 验证

如果 kubectl 可用：
```bash
kubectl apply --dry-run=client -f k8s/
```

否则进行 YAML 语法检查。

## 标签规范

所有资源使用统一标签：
```yaml
metadata:
  labels:
    app.kubernetes.io/name: <service-name>
    app.kubernetes.io/component: <component>
    app.kubernetes.io/version: <version>
```

## 输出格式

完成后输出：

```markdown
## K8s 配置已生成

**服务**: <name>
**命名空间**: <namespace>
**文件**: k8s/

### 生成的文件
- deployment.yaml — 2 副本，资源限制，健康检查
- service.yaml — ClusterIP
- ...

### 部署命令

    kubectl apply -f k8s/

### 验证

    kubectl get pods -l app.kubernetes.io/name=<name>
    kubectl logs -l app.kubernetes.io/name=<name>
```
