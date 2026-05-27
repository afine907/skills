# RBAC Patterns

## Role + RoleBinding（命名空间级）

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
  - kind: ServiceAccount
    name: my-sa
    namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## ClusterRole + ClusterRoleBinding（集群级）

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-viewer
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "endpoints"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "statefulsets"]
    verbs: ["get", "list", "watch"]
```

## 常用模式

| 场景 | 权限 |
|------|------|
| CI/CD pipeline | namespace 内 deploy 权限 |
| 监控系统 | 集群级 get/list/watch |
| 开发者 | namespace 内全权限 |
| 只读审计 | 集群级 get/list/watch |

## 权限检查

```bash
kubectl auth can-i create deployments --namespace default
kubectl auth can-i '*' '*' --as=system:serviceaccount:default:my-sa
kubectl auth can-i list pods --namespace kube-system --as=dev-user
```

## 避免 cluster-admin

不要给应用 ServiceAccount `cluster-admin`，按需分配最小权限。
