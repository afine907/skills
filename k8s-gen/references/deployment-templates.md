# Deployment & Service Templates

## Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <service-name>
  labels:
    app.kubernetes.io/name: <service-name>
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: <service-name>
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app.kubernetes.io/name: <service-name>
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
        - name: <service-name>
          image: <image>:<tag>
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
          ports:
            - containerPort: 8080
              protocol: TCP
          env:
            - name: PORT
              value: "8080"
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
```

## Service (ClusterIP)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <service-name>
  labels:
    app.kubernetes.io/name: <service-name>
spec:
  selector:
    app.kubernetes.io/name: <service-name>
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
```

## Service (NodePort)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <service-name>
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: <service-name>
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080
```

## Service (LoadBalancer)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <service-name>
spec:
  type: LoadBalancer
  selector:
    app.kubernetes.io/name: <service-name>
  ports:
    - port: 80
      targetPort: 8080
```
