# Helm 部署

使用 Helm Chart 在 Kubernetes 集群上部署 CatWiki。

## 前置要求

- Kubernetes >= 1.24
- Helm >= 3.10
- 已构建并推送的 CatWiki Docker 镜像（backend、admin、client）
- 可用的 StorageClass（用于持久化存储）

## 快速开始

### 1. 安装

```bash
# 使用默认配置安装
helm install catwiki deploy/helm -n catwiki --create-namespace

# 使用自定义配置安装
helm install catwiki deploy/helm -n catwiki --create-namespace -f my-values.yaml
```

### 2. 修改关键配置

::: warning ⚠️ 生产环境必须修改以下配置！
默认密码仅用于测试，请务必在部署前修改。
:::

创建 `my-values.yaml`：

```yaml
postgres:
  password: "your-secure-db-password"

redis:
  password: "your-secure-redis-password"

rustfs:
  accessKey: "your-rustfs-access-key"
  secretKey: "your-rustfs-secret-key"
  publicUrl: "https://files.yourdomain.com"

backend:
  secretKey: "random-string-at-least-32-chars"
  corsOrigins: '["https://admin.yourdomain.com","https://yourdomain.com"]'

admin:
  env:
    NEXT_PUBLIC_API_URL: https://api.yourdomain.com
    NEXT_PUBLIC_CLIENT_URL: https://yourdomain.com

client:
  env:
    NEXT_PUBLIC_API_URL: https://api.yourdomain.com
    NEXT_PUBLIC_ADMIN_URL: https://admin.yourdomain.com
```

### 3. 升级和卸载

```bash
# 升级（自动执行数据库迁移）
helm upgrade catwiki deploy/helm -n catwiki

# 卸载（PVC 数据会保留，不会丢失）
helm uninstall catwiki -n catwiki
```

## 架构概览

| 组件 | K8s 资源类型 | 默认镜像 | 说明 |
|------|-------------|----------|------|
| PostgreSQL | StatefulSet | `pgvector/pgvector:pg18` | 向量数据库，PVC 持久化 |
| Redis | Deployment | `redis:8.4.2` | 缓存服务，PVC 持久化 |
| RustFS | Deployment | `rustfs/rustfs:1.0.0-alpha.76` | 对象存储，PVC 持久化 |
| Backend Init | Job (Helm Hook) | `catwiki-backend:latest` | 自动数据库迁移 & 初始化 |
| Backend | Deployment | `catwiki-backend:latest` | FastAPI 后端 API |
| Admin | Deployment | `catwiki-admin:latest` | 管理后台前端 |
| Client | Deployment | `catwiki-client:latest` | 客户端前端 |
| Ingress | Ingress | — | 可选，多域名路由 |

## 配置 Ingress

默认 Ingress 未启用。通过以下配置开启并配置 HTTPS：

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  apiHost: api.yourdomain.com
  adminHost: admin.yourdomain.com
  clientHost: yourdomain.com
  tls:
    - secretName: catwiki-tls
      hosts:
        - api.yourdomain.com
        - admin.yourdomain.com
        - yourdomain.com
```

## 使用外部数据库

如已有 PostgreSQL 或 Redis，可禁用内置服务：

```yaml
postgres:
  enabled: false

redis:
  enabled: false
```

然后通过 `--set` 或自定义 values 文件配置外部连接地址。

## 数据持久化

所有 PVC 均配置了 `helm.sh/resource-policy: keep`，执行 `helm uninstall` 时数据 **不会被删除**，下次安装会自动重新绑定。

如需彻底清理数据，请手动删除 PVC：

```bash
kubectl delete pvc -l app.kubernetes.io/part-of=catwiki -n catwiki
```

## 完整参数列表

详见 Chart 目录下的 [README](https://github.com/bulolo/CatWiki/blob/main/deploy/helm/README.md) 或 `deploy/helm/values.yaml`。
