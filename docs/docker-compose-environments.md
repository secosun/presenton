# Docker Compose：生产与开发服务说明

本文说明仓库根目录 `docker-compose.yml` 中 **`production` / `development`**（及对应 GPU 变体）在**构建镜像**与**运行容器**时的差异，依据 `Dockerfile`、`Dockerfile.dev` 与 `start.js`。

## 命令对应

**建议优先使用 Compose V2**：`docker compose …`（子命令与 V1 相同，中间为空格）。旧版独立程序 **`docker-compose` 1.29.x** 与较新 Docker Engine 组合时，可能出现 **`KeyError: 'ContainerConfig'`**（见下文「常见问题」第 7 条）。

| 用途 | 构建示例 |
|------|-----------|
| 生产镜像 | `docker compose build production` |
| 开发镜像 | `docker compose build development` |
| 生产 + NVIDIA GPU | `docker compose build production-gpu` |
| 开发 + NVIDIA GPU | `docker compose build development-gpu` |

GPU 变体在 compose 中通过 `deploy.resources.reservations.devices` 申请 GPU；其余行为分别与同名的非 GPU 服务对齐（生产用 `Dockerfile`，开发用 `Dockerfile.dev`）。

---

## 日常启动（使用手册 · OpenClaw / 物化联调）

仓库根 `docker-compose.yml` 中 **`production`、`production-gpu`、`development`、`development-gpu` 均在宿主机映射 `5000:80`**。若执行**无服务名**的：

```bash
docker compose up -d
# 或
docker-compose up -d
```

Compose 会尝试**并行拉起多套主应用**，导致 **5000 端口冲突**或仅有一套实际对外，排障困难。**请显式指定要跑的一套栈。**

### 推荐：开发栈（源码挂载 + Docling）

与 **OpenClaw 多 Agent PPT 联调**、本仓库 **`Dockerfile.dev`** 场景一致时，在仓库根执行：

```bash
cd /path/to/presenton
# 首次：复制 .env.example 为 .env，按需填写 LLM、DATABASE_URL、OPENCLAW_* 等
docker compose down
docker compose up -d docling-service development
```

使用 **Compose V1** 时：

```bash
docker-compose down
docker-compose up -d docling-service development
```

- **`docling-service`**：FastAPI 物化链路依赖的 Docling 侧car；**须与主应用一并启动**。
- **`development`**：Next `dev` + FastAPI `--reload` + **`.:/app`** 挂载，改代码即生效。

### 环境变量（`.env` 建议项）

| 变量 | 说明 |
|------|------|
| **`CAN_CHANGE_KEYS`** | Compose 模板会引用；未用 UI 改密钥时可设为空 **`CAN_CHANGE_KEYS=`**，避免 “variable is not set” 警告。 |
| **`PRESENTON_PUBLIC_EXPORT_BASE`** | 可选；公网 HTTPS **origin**（**无尾斜杠**），如 `https://ppt.example.com`。设置后物化/导出 JSON 会多字段 **`download_url_public`**（与内网 **`download_url`** 同 path）。与 OpenClaw **`PRESENTON_PUBLIC_EXPORT_BASE`** 同名，便于双栈对齐。别名：**`PRESENTON_PUBLIC_BASE_URL`**。 |
| **`OPENCLAW_GATEWAY_BASE` / `OPENCLAW_GATEWAY_TOKEN`** | Presenton 容器访问 OpenClaw 网关（微信扫码等）；默认值见 `.env.example`。 |

内网下载 URL 仍由 **`PRESENTON_HOST`**、**`PRESENTON_PORT`**（默认 `192.168.3.58:5000`）参与生成，见 `servers/fastapi/utils/export_utils.py`。

### 生产栈（仅示例）

需要不可变镜像、不挂载整仓时：

```bash
docker compose up -d docling-service production
```

GPU 变体将上述主服务名换成 **`development-gpu`** 或 **`production-gpu`** 即可（仍**只选其一**，避免重复占 5000）。

### 首轮物化较慢

**冷启动**后第一次走物化时，Next 侧可能触发大量编译，异步物化在 **180s** 内未完成属常见现象；**再触发一次**或等待编译结束后再测即可。

### 与 OpenClaw 联调自检

OpenClaw 仓库根：**`PRESENTON_REQUIRED=1 ./scripts/dev-ppt-pipeline-verify.sh`**（须 Agent 容器内 MCP URL 指向本 Presenton 入口，如 `http://192.168.3.58:5000/mcp`）。

---

## 镜像构建差异

| 项目 | **production**（`Dockerfile`） | **development**（`Dockerfile.dev`） |
|------|-------------------------------|-------------------------------------|
| 应用源码 | 构建时 **`COPY`** Next.js、FastAPI、`start.js` 等进入镜像 | **不将**业务源码打入镜像；仅安装系统依赖、Python 包与 `nginx.conf` |
| Next.js | 镜像内执行 **`npm install`** 与 **`npm run build`**，产出生产构建 | 镜像内**不**执行 Next 生产构建；运行时依赖挂载目录，由 **`npm run dev`** 启动 |
| FastAPI 代码 | 随镜像发布 | 运行时来自宿主机挂载的 `.:/app` |
| **Ollama（内置）** | 当前 `production` 通过 build-arg **`INSTALL_OLLAMA: "false"`** 跳过安装，并设置 **`ENABLE_OLLAMA=false`**，启动时不执行 `ollama serve` | `Dockerfile.dev` 中 Ollama 安装脚本为**注释**，镜像内默认无内置 Ollama |
| **`production-gpu`** | 使用同一 `Dockerfile`，**未**设置 `INSTALL_OLLAMA: "false"`，默认仍会安装内置 Ollama（与 `production` 不同，若需一致可自行在 compose 中增加相同 `args`） | — |
| 宿主机 SOCKS 代理与 pip | `Dockerfile` 含在无代理环境下先安装 **PySocks** 的步骤，减轻 `*_PROXY=socks5h://...` 导致的 pip 报错 | **`Dockerfile.dev` 无**该步骤；在相同代理环境下构建 `development` 时仍可能出现 `Missing dependencies for SOCKS support`，可按生产 Dockerfile 思路增补 |

---

## 运行时卷（`volumes`）

| 项目 | **production** | **development** |
|------|----------------|-------------------|
| 数据目录 | `./app_data:/app_data` | `./app_data:/app_data` |
| 项目源码 | **不**挂载整个仓库 | **`.:/app`**（整仓挂载到容器 `/app`） |

**含义简述**

- **生产**：行为接近「不可变镜像」；日常持久化主要在 `app_data`；修改宿主机仓库代码**不会**自动进入已在跑的容器（除非重建镜像或另行挂载）。
- **开发**：本地改代码立即反映到容器内 `/app`，便于联调；首次/依赖变更时由 `start.js --dev` 触发 Next 侧 `npm install` 等逻辑。

---

## 启动与进程行为（`CMD` + `start.js`）

| 项目 | **production** | **development** |
|------|----------------|-------------------|
| 容器入口 | `node /app/start.js` | `node /app/start.js --dev` |
| Next.js | **`npm run start`**（生产模式） | **`npm run dev`**（开发模式） |
| FastAPI | `--reload false` | `--reload true`（热重载） |
| 内置 Ollama | 由镜像内 **`ENABLE_OLLAMA`** 决定；当前 `production` 构建为 `false` 时不启动 | 镜像无内置 Ollama 时不会启动；若需 Ollama 请配置 **`OLLAMA_URL`** 指向外部服务 |

---

## 环境变量（`environment`）

`production` 与 `development` 在 compose 模板中列出的变量项（如 `LLM`、`OPENAI_API_KEY`、`DATABASE_URL` 等）**一致**，均依赖 `.env` 或宿主机导出环境。**差异主要在镜像内容、挂载方式与 `start.js` 是否带 `--dev`**，而非变量键名列表本身。

`development` / `development-gpu` 额外设置 **`CYPRESS_INSTALL_BINARY=0`**，避免容器内 `npm install` 下载 Cypress 二进制（体积大、易因网络失败）。

---

## 选用建议

- 需要**可复现、可交付**的运行环境、Next 已编译进镜像 → 使用 **`production`**（或按需 `production-gpu`）。
- 需要**频繁改前端/后端源码**、热重载与挂载整仓 → 使用 **`development`**（或 `development-gpu`）。

更多关于单容器内 Nginx / FastAPI / MCP / Next 等关系，见 [deployment-architecture.md](./deployment-architecture.md)。  
镜像体积与构建时间受 Python 依赖（含 **Docling → PyTorch**）影响，说明见 [pytorch-docling.md](./pytorch-docling.md)。

---

## 常见问题

### 1. Docker：`Permission denied` / 无法连接 Docker daemon

执行 `docker-compose build …` 或 `docker compose build …` 时若出现：

- `PermissionError: [Errno 13] Permission denied`（连接 `unix:///var/run/docker.sock`）
- `Error while fetching server API version: ('Connection aborted.', PermissionError(13, 'Permission denied'))`

说明**当前终端用户无权访问 Docker 守护进程**；`docker-compose` 在连上 API 之前就会失败，与具体构建 `production` 还是 `development` 无关。

**处理办法（任选其一）**

1. **推荐（日常不用 sudo）**  
   - 将当前用户加入 `docker` 组：  
     `sudo usermod -aG docker $USER`  
   - 使组权限生效：**重新登录**、**注销后重开会话**，或在本机执行 `newgrp docker` 后**在同一 shell** 内再运行：  
     `docker-compose build <服务名>`  
   - 自检：`groups` 输出中应包含 `docker`；`docker ps` 不应再报 permission denied。

2. **临时**  
   - `sudo docker-compose build <服务名>`（需本机可交互输入 sudo 密码）。

**说明**：加入 `docker` 组后，若 IDE/Cursor 内嵌终端仍报错，多半是**该终端在加组之前已打开**、未加载新组信息；请关掉终端再开，或在新开的系统终端里执行上述命令。

### 2. Compose：`The XXX variable is not set` 警告

未提供 `.env` 或未在 shell 中 `export` 对应变量时，compose 会把 `docker-compose.yml` 里的 `${XXX}` 当成空字符串并打印 `WARNING`。**一般不会单独导致构建失败**；若需减少警告，可在项目根目录配置 `.env` 或导出相关变量。

### 3. 构建 docling 时：`THESE PACKAGES DO NOT MATCH THE HASHES`（如 dill）

多与宿主机 **`PIP_REQUIRE_HASHES=1`** 或带哈希锁定的 requirements 在构建中被继承有关。`Dockerfile` / `Dockerfile.dev` 已做缓解；详见 [pytorch-docling.md](./pytorch-docling.md) 中 **「构建失败：THESE PACKAGES DO NOT MATCH THE HASHES」** 一节。

### 4. Next.js 构建：`Downloading Cypress` / `Corrupted download`

`servers/nextjs` 将 **Cypress** 放在 **`devDependencies`** 里；`npm install` 会触发 Cypress 从 `download.cypress.io` 拉取约 **200MB** 的安装包。在 Docker 构建或弱网/代理环境下易出现**校验失败、体积远小于预期**（截断）等错误。

**生产镜像不需要在容器内跑 Cypress**。`Dockerfile` 在 `npm install` 前设置 **`ENV CYPRESS_INSTALL_BINARY=0`**，跳过二进制下载，仍保留 npm 包与 **`next build` 所需的其他 devDependencies**（如 TypeScript、Tailwind）。若需在本地或 CI 跑 E2E，请在宿主机安装依赖并正常下载 Cypress，或自行配置 `HTTP(S)_PROXY` 等，参见 [Cypress 代理说明](https://docs.cypress.io/guides/references/proxy-configuration)。

### 5. Docker 构建 pip：国内源与切回官方

`Dockerfile` / `Dockerfile.dev` 默认使用 **清华 PyPI** + **阿里云 PyTorch CPU wheels**（见 [pytorch-docling.md](./pytorch-docling.md)）。若在境外构建或镜像不可用，可在 **`docker-compose.yml`** 的 `build.args` 中覆盖 `PIP_INDEX_URL`、`TORCH_EXTRA_INDEX`，或使用：

`docker-compose build --build-arg PIP_INDEX_URL=https://pypi.org/simple --build-arg TORCH_EXTRA_INDEX=https://download.pytorch.org/whl/cpu …`

### 6. 根分区或 Docker 盘满：`No space left on device`

构建中若出现：

- `dpkg: … failed to write (No space left on device)`
- `cannot copy extracted data … to '/usr/bin/….dpkg-new'`
- `failed to write status database … '/var/lib/dpkg/status'`

说明宿主机 **`/`**（或 Docker 数据目录所在分区）**空间耗尽**，`apt-get install` 等步骤无法完成。

**处理思路**

1. 查看：`df -h /`、`docker system df`  
2. 释放空间：`docker container prune -f`、`docker image prune -af`、`docker builder prune -af`（按需，注意会删除未使用容器/镜像/构建缓存）  
3. 系统侧：`sudo apt clean`、清理 journal 与大文件；长期可 **扩容 LVM** 或迁移 Docker `data-root`。

Presenton 镜像（含 LibreOffice、Chromium、Python 栈、Next 构建）体积大，建议为 **`docker compose build`** 预留 **至少十余 GB 可用空间**。

### 7. `docker-compose up` 报错 `KeyError: 'ContainerConfig'`

较新的 Docker Engine 在镜像元数据里可能**不再提供**旧字段 **`ContainerConfig`**；独立程序 **`docker-compose` 1.29.x** 在「重建容器、合并匿名卷绑定」时仍读取该字段，于是抛出 **`KeyError: 'ContainerConfig'`**。这与 `docker-compose.yml` 内容无关。

**推荐（根治）**：安装并使用 Compose **V2 插件**：

```bash
docker compose version
docker compose up development
```

Ubuntu / Debian 上若提示没有 `compose` 子命令，可安装插件后再试：

```bash
sudo apt-get update && sudo apt-get install -y docker-compose-plugin
```

**仍坚持使用 `docker-compose` V1 时**，可先拆掉本项目旧容器再启动，有时能避开该代码路径（不保证在所有 Docker 版本上有效）：

```bash
docker-compose down --remove-orphans
docker ps -a --filter name=presenton_development --format '{{.ID}}' | xargs -r docker rm -f
docker-compose up development
```

若上述仍失败，请改用 **`docker compose`**（V2）；V1 已不再维护，无法通过改 Presenton 仓库消除该兼容性问题。
