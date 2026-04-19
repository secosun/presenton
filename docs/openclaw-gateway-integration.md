# OpenClaw Gateway 集成配置文档

## 概述

Presenton 与 OpenClaw Gateway 集成实现微信扫码绑定功能，支持 Agent 分布式通信。

## 架构设计

### 网络拓扑

```
┌─────────────────────────────────────────────────────────┐
│                     用户浏览器                           │
│                http://localhost:5000                    │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                  Docker 容器网络                         │
│                                                          │
│  ┌──────────┐ 80    ┌──────────┐ 3000  ┌────────────┐  │
│  │  Nginx   │──────▶│ Next.js  │──────▶│  API Route │  │
│  └──────────┘       └──────────┘       └──────┬─────┘  │
│                                                │        │
│                                                ▼        │
│                                      host.docker.internal│
│                                                :18789   │
└────────────────────────────────────────────────┬────────┘
                                                 │
┌────────────────────────────────────────────────▼────────┐
│                    宿主机网络                           │
│              OpenClaw Gateway :18789                   │
└─────────────────────────────────────────────────────────┘
```

### 环境变量设计

由于 Next.js 的 `NEXT_PUBLIC_*` 变量会在构建时被静态内联到代码中，无法通过运行时环境变量覆盖，因此采用双变量设计：

| 变量名 | 作用域 | 说明 |
|--------|--------|------|
| `OPENCLAW_GATEWAY_BASE` | 服务端 | 纯服务端 API 使用，运行时可修改 |
| `OPENCLAW_GATEWAY_TOKEN` | 服务端 | 纯服务端 API 使用，运行时可修改 |
| `NEXT_PUBLIC_OPENCLAW_GATEWAY_BASE` | 前端 + 构建 | 前端代码直接使用 |
| `NEXT_PUBLIC_OPENCLAW_GATEWAY_TOKEN` | 前端 + 构建 | 前端代码直接使用 |

在 API Route 中的优先级：
1. 优先使用 `OPENCLAW_GATEWAY_*`（运行时环境变量）
2. 回退到 `NEXT_PUBLIC_OPENCLAW_GATEWAY_*`（构建时内联值）
3. 最终回退到生产环境默认值

## 配置方法

### Docker 环境（推荐）

`docker-compose.yml` 已预配置内网访问：

```yaml
services:
  production:
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - OPENCLAW_GATEWAY_BASE=http://host.docker.internal:18789
      - OPENCLAW_GATEWAY_TOKEN=openclaw-distributed-secret-key
      - NEXT_PUBLIC_OPENCLAW_GATEWAY_BASE=http://host.docker.internal:18789
      - NEXT_PUBLIC_OPENCLAW_GATEWAY_TOKEN=openclaw-distributed-secret-key
```

### 开发环境

```yaml
services:
  development:
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - OPENCLAW_GATEWAY_BASE=http://host.docker.internal:18789
      - OPENCLAW_GATEWAY_TOKEN=openclaw-distributed-secret-key
```

### 自定义 Gateway 地址

如果 Gateway 不在本机，修改环境变量：

```yaml
environment:
  - OPENCLAW_GATEWAY_BASE=https://your-gateway-domain.com
  - OPENCLAW_GATEWAY_TOKEN=your-secret-token
  - NEXT_PUBLIC_OPENCLAW_GATEWAY_BASE=https://your-gateway-domain.com
  - NEXT_PUBLIC_OPENCLAW_GATEWAY_TOKEN=your-secret-token
```

## 启动步骤

### 1. 启动 OpenClaw Gateway

在 `openclawcluster` 目录：

```bash
cd ../openclawcluster
docker-compose -f docker-compose.distributed.yml up -d
```

验证 Gateway 运行：
```bash
curl http://localhost:18789/healthz
```

### 2. 启动 Presenton

```bash
cd presenton

# 生产环境
docker-compose up -d production

# 开发环境
docker-compose up -d development
```

### 3. 验证集成

```bash
# 测试二维码生成
curl http://localhost:5000/api/openclaw/weixin/qrcode

# 测试扫码页面代理
curl http://localhost:5000/api/openclaw/weixin/scan
```

## API 端点

### 二维码生成

**GET** `/api/openclaw/weixin/qrcode`

返回二维码图片的 base64 编码：
```json
{
  "qrCode": "data:image/png;base64,iVBORw0KGgo...",
  "sessionKey": "uuid",
  "message": "使用微信扫描二维码",
  "waitPath": "/__openclaw__/weixin/login/wait",
  "expireTime": 1713500000000
}
```

### 状态轮询

**POST** `/api/openclaw/weixin/status`

请求体：
```json
{
  "sessionKey": "uuid-from-qrcode"
}
```

响应：
```json
{
  "status": "waiting|scanned|success|expired|error",
  "message": "等待扫码...",
  "data": {}
}
```

### 扫码页面代理

**GET** `/api/openclaw/weixin/scan`

代理返回 Gateway 的原始扫码 HTML 页面。

## 故障排查

### 问题：二维码接口返回 "无法获取二维码数据"

**可能原因：**
1. Gateway 未启动 - 检查 `http://localhost:18789/healthz`
2. 容器内无法访问宿主机 - 验证 `extra_hosts` 配置
3. Token 不匹配 - 检查两边的 token 配置

**诊断命令：**
```bash
# 进入容器测试
docker exec presenton_production_1 curl -s http://host.docker.internal:18789/healthz
```

### 问题：容器内无法解析 host.docker.internal

**解决方案：**
Linux Docker 需要显式配置 `extra_hosts`（已在 docker-compose.yml 中配置）。

### 问题：Next.js 构建后仍然使用旧地址

**原因：**
`NEXT_PUBLIC_*` 变量在 `npm run build` 时被固化到代码中。

**解决方案：**
1. 使用无 `NEXT_PUBLIC_` 前缀的服务端变量
2. 重新构建镜像：`docker-compose build --no-cache production`

### 问题：开发环境前端无法访问 Gateway

**原因：**
前端代码在用户浏览器中运行，`host.docker.internal` 只在容器内有效。

**解决方案：**
开发环境配置为用户浏览器可访问的地址，如 `http://localhost:18789`。

## 安全注意事项

1. **Token 保密**：不要将真实的 Gateway Token 提交到代码仓库
2. **HTTPS**：生产环境 Gateway 应使用 HTTPS
3. **内网隔离**：Gateway 管理端口应限制在内网访问
4. **CORS**：配置 Gateway 的 CORS 策略只允许信任的域名

## 参考

- [OpenClaw Gateway 分布式部署文档](../openclawcluster/docs/gateway/distributed-deployment-guide.md)
- [Presenton 服务架构](./service-architecture.md)
