# OpenClaw / MCP / 物化 参考

本文档汇总 **Agent 集成 Presenton 时的架构约定、MCP 暴露方式、环境变量与接口选择**，与仓库内 `openclaw-mcp-integration-guide.md`、`external-agent-materialize.md` 互补；实现细节以代码为准。

---

## 1. 架构角色

| 组件 | 职责 |
|------|------|
| **OpenClaw（或其它 Agent）** | 推理、内容结构、多步编排；不依赖 Presenton 内建 LLM 完成「从一句话到 PPT」也可行。 |
| **Presenton（本仓库）** | **落地**：在收到结构化 `MaterializePresentationRequest` 后，校验模板/版式、写库、经 Next 导出 **pptx/pdf**；同时提供文件、主题、Webhook 等已注册能力。 |

物化服务 **不替代** 服务端大模型；若只走物化，大脑在外部是预期用法。

---

## 2. MCP 如何暴露接口

- **MCP 服务**：`servers/fastapi/mcp_server.py`，使用 **FastMCP.from_openapi**，HTTP 客户端以 **`PRESENTON_API_BASE_URL`** 为基址实际调用 **FastAPI**（与 Nginx 统一入口时多为 `http://<host>:5000` 或经代理后的地址）。
- **OpenAPI 来源（默认）**：`PRESENTON_MCP_OPENAPI_SOURCE=app` 时，从 **`api.main:app` 的 `app.openapi()`** 生成工具列表，与 **`/openapi.json`、Swagger `/docs` 一致**；新增注册到 `app` 的路由会**自动**出现在 MCP 中，**无需**手改 `openai_spec.json`。
- **兼容模式**：`PRESENTON_MCP_OPENAPI_SOURCE=file`（或 `json` / `legacy`）时，仅加载同目录下 **`openai_spec.json`（物化子集）**，用于离线、调试或旧集成。

**跨主机时**：MCP 进程与 FastAPI 不同机，须设置 `PRESENTON_API_BASE_URL` 指向可访问的 Presenton API 基址（无尾斜杠）。

---

## 3. 物化（落地）在 API 上最少需要什么

1. **二选一**  
   - **同步**：`POST /api/v1/ppt/presentation/materialize`  
   - **异步**：`POST /api/v1/ppt/presentation/materialize/async` + `GET /api/v1/ppt/presentation/materialize/jobs/{job_id}` 轮询至 `completed` 或 `failed`。
2. **版式与 JSON Schema**：每条 slide 的 `layout_id` 与 `content` 必须符合模板定义。  
   原先 **不在** 精简 FastAPI 的「layout 专用路由」里，而来自 **Next** 的 `/api/template` / `/api/templates`。现已在 FastAPI 侧做 **代理**（见下节），便于与 MCP 同域、同 OpenAPI 发现。

---

## 4. Next 侧「有用 API」的 MCP 暴露方式

为简化 Agent 只连 **FastAPI 基址** 即可发现能力，在 FastAPI 增加 **对 Next 的只读 JSON 代理**（`httpx` 转发；Next 不可达时返回 502 说明）：

| FastAPI 路径 | 透传至 Next | `operationId` | 说明 |
|--------------|---------------|---------------|------|
| `GET /api/v1/nextjs/template?group=` | `GET /api/template?group=` | `get_nextjs_template` | 某模板下全部 slide 的 `id` / `name` / `json_schema`；Next 内可能走 headless，**较慢**，默认超时 300s。 |
| `GET /api/v1/nextjs/templates` | `GET /api/templates` | `list_nextjs_presentation_templates` | 枚举 `presentation-templates` 下模板目录、layout 文件名与 settings。 |
| `GET /api/v1/nextjs/has-required-key` | `GET /api/has-required-key` | `get_nextjs_has_openai_key` | 仅返回是否配置 OpenAI 密钥，**不**含密钥；物化不依赖此项。 |

实现文件：`servers/fastapi/api/v1/nextjs_proxy/router.py`（Desktop/Electron 树中有同名模块以保持结构一致；以实际运行的 `api.main` 为准）。

**注意**：Nginx/容器内对 Next 的访问基址应与其它模块一致，见环境变量 `PRESENTON_NEXTJS_BASE_URL`（下节）。物化核心路径 `get_layout_by_name` 与 `export_utils` 中对 Next 的 HTTP 调用已改为使用同一基址与超时，避免与 MCP 各配各的。

---

## 5. 主要环境变量

| 变量 | 作用 |
|------|------|
| `PRESENTON_API_BASE_URL` | MCP 子进程里 **httpx** 访问 FastAPI 的基址。 |
| `PRESENTON_MCP_OPENAPI_SOURCE` | `app`（默认，全量 OpenAPI）或 `file`（仅 `openai_spec.json`）。 |
| `PRESENTON_NEXTJS_BASE_URL` | FastAPI 访问 **Next** 的基址（默认 `http://127.0.0.1`，同机常无端口、走 80 反代到 Next 的 `/api/*`）。 |
| `PRESENTON_NEXTJS_HTTP_TIMEOUT` | 调 Next（尤其 `/api/template`）的秒数，默认 `300`。 |
| `PRESENTON_HTTP_TIMEOUT` | MCP 侧 httpx 客户端总超时。 |

示例见根目录 **`.env.example`**。

---

## 6. API 清单与说明（归档：`servers/fastapi` 的 `api.main`）

下表为 **当前精简后端** 在 `app` 上注册、并进入 `openapi.json` / **MCP（`PRESENTON_MCP_OPENAPI_SOURCE=app` 时）** 的 HTTP 面。**权威列表**以部署实例的 `GET /openapi.json` 为准；`electron/servers/fastapi` 的 `app` 可能**额外**包含更多路由，勿与此表逐条对号入座。

**「物化相关」列**：仅表示与「结构化落地→pptx/pdf」工作流的**推荐程度**；`必用` 指完成一次物化**至少**要用的接口族（在同步/异步、是否先查 schema 上仍有组合）。

| 方法 | 路径 | 说明 | 物化 / OpenClaw |
|------|------|------|-----------------|
| `GET` | `/api/v1/healthz` | 探活，返回服务存活 JSON。 | 可选（运维/探针） |
| `GET` | `/api/v1/mock/presentation-generation-completed` | 返回**模拟**成功物化/导出结构，用于联调。 | 调试用，非生产物化 |
| `GET` | `/api/v1/mock/presentation-generation-failed` | 返回**模拟**失败结构。 | 调试用 |
| `POST` | `/api/v1/ppt/files/upload` | 多文件上传，返回临时路径列表。 | 可选（素材/文档进管线） |
| `POST` | `/api/v1/ppt/files/decompose` | 对路径列表做解析，产出可读的分解结果（中间文本等）。 | 可选 |
| `POST` | `/api/v1/ppt/files/update` | 以 multipart 覆写某临时文件。 | 可选 |
| `POST` | `/api/v1/ppt/fonts/upload` | 上传自定义字体，供 PPTX 等导出使用。 | 可选 |
| `GET` | `/api/v1/ppt/fonts/uploaded` | 列出已上传字体。 | 可选 |
| `DELETE` | `/api/v1/ppt/fonts/{font_id}` | 删除字体。 | 可选 |
| `GET` | `/api/v1/ppt/icons/search` | 关键词搜索可用图标名/资源。 | 可选（做 slide 内容时） |
| `GET` | `/api/v1/ppt/presentation/all` | 列出已保存的演示。 | 可选（复用/排查） |
| `GET` | `/api/v1/ppt/presentation/{id}` | 按 ID 读取单份演示与 slides。 | 可选 |
| `DELETE` | `/api/v1/ppt/presentation/{id}` | 删除演示。 | 可选 |
| `POST` | `/api/v1/ppt/presentation/export/pptx` | 请求体为 **PptxPresentationModel**，在侧端生成并保存 **pptx 文件路径**（不经过 Next 的 `presentation_to_pptx_model` 链时用途不同）。 | 与标准物化/导出链**并列**的另一种导出入口；一般物化用下行两条之一即可 |
| `POST` | `/api/v1/ppt/presentation/export` | 对**已存在** `id` 再导出为 pptx 或 pdf（经 Next 转换链 + 本地落盘/URL）。 | 可选（已有库中演示时） |
| `POST` | `/api/v1/ppt/presentation/materialize` | **同步物化**：提交 `MaterializePresentationRequest` → 写库 + 导出；无服务端 LLM。 | **必用**（与异步二选一） |
| `POST` | `/api/v1/ppt/presentation/materialize/async` | **异步物化**，返回 `job_id`（202）。 | **必用**（与同步二选一） |
| `GET` | `/api/v1/ppt/presentation/materialize/jobs/{job_id}` | 轮询任务状态/结果/错误。 | 异步时 **必用** |
| `POST` | `/api/v1/ppt/theme/generate` | 根据主色/背景等生成 V3 主题色板 `ThemeData`。 | 可选（换肤/主题，不阻物化） |
| `GET` | `/api/v1/ppt/themes/all` | 列出用户主题。 | 可选 |
| `GET` | `/api/v1/ppt/themes/default` | 默认主题信息。 | 可选 |
| `POST` | `/api/v1/ppt/themes/create` | 创建主题。 | 可选 |
| `PATCH` | `/api/v1/ppt/themes/update/{theme_id}` | 更新主题。 | 可选 |
| `DELETE` | `/api/v1/ppt/themes/delete/{theme_id}` | 删除主题。 | 可选 |
| `POST` | `/api/v1/webhook/subscribe` | 订阅事件（如物化完成）回调 URL。 | 可选（事件驱动集成） |
| `DELETE` | `/api/v1/webhook/unsubscribe` | 按订阅 ID 取消。 | 可选 |
| `GET` | `/api/v1/nextjs/template?group=` | 代理到 Next，返回某模板下各 slide 的 `id` / `name` / `json_schema`。 | **建议**（填 `content` 前对照 schema） |
| `GET` | `/api/v1/nextjs/templates` | 代理到 Next，枚举 `presentation-templates` 下模板与 layout 文件。 | **建议**（选 `template` 名） |
| `GET` | `/api/v1/nextjs/has-required-key` | 代理到 Next，仅返回是否配置 OpenAI 密钥。 | 可选（与纯物化无关） |

**数量**：上表为 **29** 个 **HTTP 操作**（`方法` + `路径` 一行一条）。`openapi.json` 里的 `paths` **键**数量通常 **更少**（同一路径下可挂 `get` / `post` 等多个方法，只算**一条 path**）。以运行实例为准可在 Swagger `/docs` 或解析 OpenAPI 统计 operation 数。

**物化最小编集（概念上）**  

1. `GET .../nextjs/templates` 与 `GET .../nextjs/template?group=`（**建议**，用于合法 `template` 与每页 `layout_id`/`content`）。  
2. `POST .../materialize` **或** `POST .../materialize/async` + `GET .../materialize/jobs/{job_id}`。  

其它列均为加强能力或运维/联调。

---

## 7. 与 Electron 后端的差异

若使用 **`electron/servers/fastapi` 的 `app`**，路由集合**可能更多**（大模型、模板库、多图等）；生产/容器镜像常用本仓库 `servers/fastapi` 的精简 `router`。**以实际运行进程的 OpenAPI 为准。**

---

## 8. 相关文档

- 本文 **§6** — `servers/fastapi` **API 清单与物化相关度**（与 OpenAPI 同步维护的主归档）。  
- [openclaw-mcp-integration-guide.md](./openclaw-mcp-integration-guide.md) — OpenClaw 侧 MCP 配置、URL、Nginx 关系。  
- [external-agent-materialize.md](./external-agent-materialize.md) — 外部 Agent 物化接口、与 MCP 物化操作对应关系。  
- [service-architecture.md](./service-architecture.md) — 服务端口与职责概览。

---

## 9. 变更历史（本参考文档所覆盖的近期变更摘要）

- MCP 默认使用 **全量** `app.openapi()`，物化、其它 FastAPI 路由、以及 **`/api/v1/nextjs/*` 代理** 一并供 Agent 发现。  
- 新增 **Next 代理**与 **`PRESENTON_NEXTJS_BASE_URL` / `PRESENTON_NEXTJS_HTTP_TIMEOUT`**。  
- **物化/导出**内对 `localhost` 写死的 Next 地址，改为可配置的 **`get_nextjs_base_url()`** 等（见 `utils/get_env.py`、`get_layout_by_name.py`、`export_utils.py`）。  
- FastAPI 应用元信息中补充 `title` / `description`，便于在 OpenAPI/MCP 中阅读服务说明。  
- 本文 **§6** 归档 **`servers/fastapi` 当前 `api.main` 的 HTTP 操作清单**（含 Next 代理），并区分物化工作流下的必用/建议/可选。

（日期以你本地合入/发布记录为准。）
