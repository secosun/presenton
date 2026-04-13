# 为何需要 PyTorch（与 Docling 的关系）

Presenton 的后端**并未**把 PyTorch当作「自研大模型训练框架」直接使用；镜像与 `pyproject.toml` 中出现 PyTorch，是因为 **文档解析库 Docling 依赖 PyTorch**。

## 依赖关系

1. **`servers/fastapi/pyproject.toml`** 声明 **`docling>=2.43.0`**，并通过 **`https://download.pytorch.org/whl/cpu`** 作为额外索引，便于在 **CPU** 环境安装与 Docling 匹配的 torch 系列 wheel（体积与 GPU 版策略由上游包决定）。
2. **`Dockerfile` / `Dockerfile.dev`** 中通过 **`pip install docling`** 并配置 **PyPI 主索引 + PyTorch CPU 额外索引**，安装 Docling 及其 **PyTorch（CPU）** 等依赖。

### 国内镜像（默认）

镜像构建默认使用：

- **主索引**：`https://pypi.tuna.tsinghua.edu.cn/simple`（清华）  
- **PyTorch CPU wheel 额外索引**：`https://mirrors.aliyun.com/pytorch-wheels/cpu`（阿里云，替代 `download.pytorch.org/whl/cpu`）

在 `Dockerfile` / `Dockerfile.dev` 中可通过 **`ARG PIP_INDEX_URL`**、**`ARG TORCH_EXTRA_INDEX`** 覆盖，例如恢复官方：

```bash
docker build --build-arg PIP_INDEX_URL=https://pypi.org/simple \
  --build-arg TORCH_EXTRA_INDEX=https://download.pytorch.org/whl/cpu .
```

`docker-compose` 可在对应服务的 **`build.args`** 中写入上述变量。

## 在业务里做什么

- **`servers/fastapi/services/docling_service.py`** 使用 Docling 的 **`DocumentConverter`**，支持 **PDF、PPTX、DOCX** 等格式，并 **`export_to_markdown()`** 转为 Markdown。
- **`documents_loader`** 等流程在用户**上传文档生成演示**时调用该服务。

Docling 内部使用基于深度学习的版面与结构等能力（随 Docling 版本演进），这些能力通常建立在 **PyTorch** 之上，因此会安装 **`torch`** 等包。

## 与 LLM 的关系（概念区分）

| 能力 | 常见实现 | 与 PyTorch 的关系 |
|------|-----------|-------------------|
| 幻灯片文案 / 结构化生成（OpenAI、Ollama、Gemini 等） | HTTP API 调用云端或外部服务 | **通常不**在 Presenton 进程内加载 PyTorch 推理栈 |
| 上传的 Office/PDF → Markdown | **Docling** | **会**通过 Docling 引入 PyTorch |

## 若希望去掉 PyTorch

需要**移除或替换 Docling** 及其文档解析路径，并处理所有引用（例如 `DoclingService`、`documents_loader`）。这不是删除一行 `pip install` 即可完成的轻量改动，属于产品能力与依赖结构的变更。

## 构建失败：`THESE PACKAGES DO NOT MATCH THE HASHES`（例如 dill）

在 `docker-compose build` / `docker build` 安装 **docling** 时若出现类似：

`ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE`  
（涉及 **`dill`** 等传递依赖、`Expected sha256 … Got …`）

常见原因包括：

1. **宿主机或 CI 设置了 `PIP_REQUIRE_HASHES=1`**（或等效配置），构建被继承进镜像层，pip 对未在本地 requirements 中列哈希的传递依赖仍做校验，导致失败。  
2. 使用了带 **`--require-hashes`** 的 requirements/constraints，与当前解析到的 wheel 不一致。

**仓库内处理**：`Dockerfile` / `Dockerfile.dev` 已设置 **`ENV PIP_REQUIRE_HASHES=0`**、**`PIP_DISABLE_PIP_VERSION_CHECK=1`**；安装 docling 时在同一 shell 内 **`unset PIP_CONSTRAINT`**、清空 **`HTTP(S)_PROXY` / `ALL_PROXY`**，并加上 **`--trusted-host`**（减轻企业代理 / SOCKS 上 TLS 中断导致的 `SSLEOFError`）。若构建机**必须**全程走代理才能上网，请勿在宿主机对 Docker 注入会截断 TLS 的 SOCKS；可改用 **HTTP/HTTPS 代理**，或在能直连 PyPI 的网络下构建。

若你使用**自定义 Dockerfile** 或额外 `COPY requirements.txt`，请自行去掉冲突的哈希约束，或在构建前取消导出 `PIP_REQUIRE_HASHES` / `PIP_CONSTRAINT`。

### 构建 docling 时：`Read timed out` / `ReadTimeoutError`（files.pythonhosted.org）

从 PyPI 拉 **较大 wheel**（如 `docling_parse`）时，若网速很慢（例如十几 kB/s），pip 默认 **socket 超时偏短**，会在下载中途报 **`Read timed out`**。

**仓库内处理**：`Dockerfile` / `Dockerfile.dev` 已设置较大的 **`PIP_DEFAULT_TIMEOUT`**，安装 docling 时使用 **`--retries 15 --default-timeout=3600`**，并为 **`download-r2.pytorch.org`**（PyTorch CDN，与 `download.pytorch.org` 不同）加入 **`--trusted-host`**，且 **`||` 连续重试最多三次**。若构建日志里的 `pip` 命令仍无上述参数，说明命中了**旧构建缓存**，请执行 **`docker-compose build --no-cache development`**（或 `production`）后再试。若仍超时，请在网络较好时段构建，或配置可达的 **PyPI / PyTorch 镜像**。

## 相关文件

- `servers/fastapi/pyproject.toml` — Docling 与 PyTorch CPU 索引
- `servers/fastapi/services/docling_service.py` — Docling 封装
- `servers/fastapi/services/documents_loader.py` — 调用 Docling 解析
- `Dockerfile`、`Dockerfile.dev` — `pip install docling` 与 extra-index
