# 服务拆分架构说明

## 架构概述

本项目已拆分为两个独立的 Docker 服务，通过 HTTP API 进行通信：

```
┌─────────────────────────────────────┐     ┌─────────────────────────────────────┐
│   presenton_main (主服务)           │────▶│   presenton_docling (文档解析服务)  │
│   体积：~5-6GB                      │ HTTP│   体积：~6-7GB                      │
├─────────────────────────────────────┤     ├─────────────────────────────────────┤
│ • LibreOffice (PPTX→PDF 转换)       │     │ • docling                           │
│ • pdfplumber (PDF→图片/文本提取)     │     │ • torch CPU                         │
│ • chromium (浏览器截图)              │     │ • transformers 等 ML 依赖             │
│ • Next.js 前端                      │     │                                     │
│ • PPT 生成核心逻辑                  │     │ API:                                │
│ • 大纲生成                          │     │ • POST /parse (PDF/DOCX/PPTX→MD)    │
│                                     │     │ • POST /parse/upload (上传解析)      │
└─────────────────────────────────────┘     └─────────────────────────────────────┘
```

## 服务职责

### 主服务 (`production`)
- **端口**: 5000 (HTTP), 8001 (MCP)
- **Dockerfile**: `Dockerfile`
- **主要功能**:
  - PPT/PDF 生成核心逻辑
  - 大纲生成 (调用 LLM)
  - PDF 截图提取 (使用 pdfplumber)
  - PPTX→PDF 转换 (使用 LibreOffice)
  - Next.js 前端服务

### 文档解析服务 (`docling-service`)
- **端口**: 8001
- **Dockerfile**: `Dockerfile.docling`
- **主要功能**:
  - PDF → Markdown 转换
  - DOCX → Markdown 转换
  - PPTX → Markdown 转换

## Docker Compose 使用

### 启动完整服务（推荐）

```bash
# 启动所有服务（包括 docling 解析服务）
docker compose up production

# 或后台运行
docker compose up -d production
```

### 仅启动主服务（无文档解析功能）

```bash
# 临时禁用 docling 服务
docker compose up --no-deps production
```

### 独立构建 docling 服务

```bash
docker compose build docling-service
docker compose up docling-service
```

## 配置说明

### 环境变量

主服务需要配置 `DOCLING_SERVICE_URL` 环境变量指向文档解析服务：

```yaml
environment:
  - DOCLING_SERVICE_URL=http://docling-service:8001
```

如在本地开发环境使用，可设置为：
```bash
export DOCLING_SERVICE_URL=http://localhost:8001
```

### 网络配置

两个服务通过 `presenton-network` 桥接网络通信。

## 开发环境

开发环境 (`development`) 也需要 docling 服务支持：

```bash
# 启动开发环境（包含 docling 服务）
docker compose up development

# 开发环境 GPU 支持
docker compose up development-gpu
```

## API 调用示例

### 文档解析 API

```python
import httpx

# 通过文件路径解析
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://docling-service:8001/parse",
        params={"file_path": "/path/to/document.pdf"}
    )
    result = response.json()
    markdown = result["markdown"]

# 通过文件上传解析
async with httpx.AsyncClient() as client:
    with open("document.pdf", "rb") as f:
        response = await client.post(
            "http://docling-service:8001/parse/upload",
            files={"file": f}
        )
        result = response.json()
        markdown = result["markdown"]
```

## 健康检查

```bash
# 检查 docling 服务健康状态
curl http://localhost:8001/health

# 返回：{"status": "healthy", "service": "docling-service"}
```

## 故障排查

### docling 服务不可用

如果主服务报告 "Docling service unavailable"：

1. 检查 docling 服务是否运行：
   ```bash
   docker compose ps
   ```

2. 查看 docling 服务日志：
   ```bash
   docker compose logs docling-service
   ```

3. 重启 docling 服务：
   ```bash
   docker compose restart docling-service
   ```

### 构建 docling 服务失败

docling 服务包含 PyTorch 等大型依赖，构建可能失败：

```bash
# 使用国内镜像源
docker compose build --build-arg PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
                     --build-arg TORCH_EXTRA_INDEX=https://mirrors.aliyun.com/pytorch-wheels/cpu \
                     docling-service
```

## 镜像体积对比

| 服务 | 镜像体积 |
|------|---------|
| `presenton_production` (主服务) | ~5-6 GB |
| `presenton_docling` (解析服务) | ~6-7 GB |
| **总计** | **~11-13 GB** |

相比之前单镜像 10.9GB，拆分后总容积略有增加（约 1-2GB），这是因为：
- Docker 层缓存开销
- 两个基础镜像的重复部分

**优势**：
- 可独立扩展/缩放
- 可按需部署（不需要文档解析功能时可不启动 docling 服务）
- 更清晰的服务边界
- 主服务镜像体积减少约 50%
