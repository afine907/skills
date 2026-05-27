# ConfigMap & Secret Templates

## ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: <service-name>-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  DATABASE_HOST: "db.example.com"
```

### 挂载为环境变量

```yaml
spec:
  containers:
    - envFrom:
        - configMapRef:
            name: <service-name>-config
```

### 挂载为文件

```yaml
spec:
  containers:
    - volumeMounts:
        - name: config-volume
          mountPath: /app/config
  volumes:
    - name: config-volume
      configMap:
        name: <service-name>-config
```

## Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <service-name>-secret
type: Opaque
stringData:
  DATABASE_PASSWORD: "changeme"
  API_KEY: "secret-key"
```

### 挂载为环境变量

```yaml
spec:
  containers:
    - envFrom:
        - secretRef:
            name: <service-name>-secret
```

## Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: <namespace>
  labels:
    app.kubernetes.io/part-of: <project>
```
