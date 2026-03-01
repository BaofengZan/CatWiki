# CatWiki Helm Chart

使用 Helm 在 Kubernetes 上部署 CatWiki 智能知识库管理平台。

## 前置要求

- Kubernetes >= 1.24
- Helm >= 3.10
- 已构建并推送的 CatWiki Docker 镜像（backend、admin、client）
- 可用的 StorageClass（用于 PVC 持久化）

## 快速开始

```bash
# 1. 安装（使用默认配置）
helm install catwiki deploy/helm -n catwiki --create-namespace

# 2. 自定义配置安装
helm install catwiki deploy/helm -n catwiki --create-namespace -f my-values.yaml

# 3. 升级
helm upgrade catwiki deploy/helm -n catwiki

# 4. 卸载
helm uninstall catwiki -n catwiki
```

## 架构概览

| 组件 | K8s 资源 | 默认镜像 | 说明 |
|------|----------|----------|------|
| PostgreSQL | StatefulSet | `pgvector/pgvector:pg18` | 向量数据库，PVC 持久化 |
| Redis | Deployment | `redis:8.4.2` | 缓存服务，PVC 持久化 |
| RustFS | Deployment | `rustfs/rustfs:1.0.0-alpha.76` | 对象存储，PVC 持久化 |
| Backend Init | Job (Helm Hook) | `catwiki-backend:latest` | 数据库迁移 & 初始化 |
| Backend | Deployment | `catwiki-backend:latest` | FastAPI 后端 API |
| Admin | Deployment | `catwiki-admin:latest` | 管理后台前端 |
| Client | Deployment | `catwiki-client:latest` | 客户端前端 |
| Ingress | Ingress | — | 可选，多域名路由 |

## 关键配置项

> ⚠️ **生产环境必须修改以下敏感配置！**

```yaml
# values.yaml 中需要修改的关键项：

postgres:
  password: "your-secure-db-password"       # 数据库密码

redis: {}

rustfs:
  accessKey: "your-rustfs-access-key"       # 对象存储访问密钥
  secretKey: "your-rustfs-secret-key"       # 对象存储密钥
  publicUrl: "https://files.yourdomain.com" # 公网访问地址

backend:
  secretKey: "random-string-at-least-32-chars"  # JWT 签名密钥
  corsOrigins: '["https://admin.yourdomain.com","https://yourdomain.com"]'
```

## 完整参数列表

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `global.timezone` | `Asia/Shanghai` | 时区 |
| `global.imagePullPolicy` | `IfNotPresent` | 镜像拉取策略 |
| `global.imageRegistry` | `""` | 全局镜像仓库前缀 |
| `global.imagePullSecrets` | `[]` | 镜像拉取 Secret |
| **PostgreSQL** | | |
| `postgres.enabled` | `true` | 是否部署内置 PostgreSQL |
| `postgres.image.tag` | `pg18` | PostgreSQL 版本 |
| `postgres.database` | `catwiki` | 数据库名 |
| `postgres.user` | `postgres` | 数据库用户 |
| `postgres.password` | `postgres` | 数据库密码 |
| `postgres.persistence.size` | `10Gi` | 存储大小 |
| `postgres.persistence.storageClass` | `""` | StorageClass |
| **Redis** | | |
| `redis.enabled` | `true` | 是否部署内置 Redis |
| `redis.image.tag` | `8.4.2` | Redis 版本 |
| `redis.persistence.size` | `2Gi` | 存储大小 |
| **RustFS** | | |
| `rustfs.enabled` | `true` | 是否部署内置 RustFS |
| `rustfs.persistence.dataSize` | `20Gi` | 数据存储大小 |
| `rustfs.persistence.logsSize` | `2Gi` | 日志存储大小 |
| **Backend** | | |
| `backend.replicaCount` | `1` | 副本数 |
| `backend.secretKey` | `change-me...` | JWT 密钥 |
| `backend.corsOrigins` | `[...]` | CORS 域名列表 |
| `backend.service.port` | `3000` | 服务端口 |
| **Admin** | | |
| `admin.replicaCount` | `1` | 副本数 |
| `admin.service.port` | `8001` | 服务端口 |
| **Client** | | |
| `client.replicaCount` | `1` | 副本数 |
| `client.service.port` | `8002` | 服务端口 |
| **Ingress** | | |
| `ingress.enabled` | `false` | 是否启用 Ingress |
| `ingress.className` | `nginx` | Ingress Class |
| `ingress.apiHost` | `api.catwiki.cn` | API 域名 |
| `ingress.adminHost` | `admin.catwiki.cn` | 管理后台域名 |
| `ingress.clientHost` | `catwiki.cn` | 客户端域名 |
| `ingress.tls` | `[]` | TLS 配置 |

## 启用 Ingress 示例

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  apiHost: api.catwiki.cn
  adminHost: admin.catwiki.cn
  clientHost: catwiki.cn
  tls:
    - secretName: catwiki-tls
      hosts:
        - api.catwiki.cn
        - admin.catwiki.cn
        - catwiki.cn
```

## 使用外部数据库

如需使用已有的 PostgreSQL/Redis，可禁用内置服务并在 ConfigMap/Secret 中指定连接信息：

```yaml
postgres:
  enabled: false    # 禁用内置 PostgreSQL

redis:
  enabled: false    # 禁用内置 Redis
```

然后通过 `--set` 或自定义 values 文件配置外部连接地址。
