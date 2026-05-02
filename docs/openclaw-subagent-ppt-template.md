# OpenClaw 子 Agent：`ppt-template` 行为约束

本文档面向 **OpenClaw 编排下的子 Agent `ppt-template`**，约束其在对接 **Presenton** 时的职责边界、调用顺序与数据契约，避免物化失败（400 / 422 / 502）。实现与接口细节以本仓库代码为准：`servers/fastapi`、`servers/fastapi/mcp_server.py`、`servers/nextjs/app/presentation-templates`。

---

## 0. OpenClaw 通过 MCP 访问（必读）

| 项目 | 说明 |
|------|------|
| **访问链** | OpenClaw → **MCP 工具**（`servers/fastapi/mcp_server.py`，FastMCP `from_openapi`）→ **HTTP 调用 `PRESENTON_API_BASE_URL`** 上的 FastAPI → FastAPI 再访问 Next（模板 schema、导出等）。 |
| **子 Agent 约定** | `ppt-template` **只应通过 MCP 暴露的工具**读写 Presenton；不要假设能直接 `curl` 内网地址，也不要绕过 MCP 手拼 URL（除非运维明确提供直连且与 OpenClaw 配置一致）。 |
| **工具名** | MCP 工具由 **OpenAPI `operationId`** 派生；OpenClaw 的 `tools.allow` 常为 **`presenton__<operationId>`** 形式（与运行实例 `tools/list` 对齐，见 `scripts/verify-presenton-mcp-allow.mjs`）。 |
| **OpenAPI 来源** | `PRESENTON_MCP_OPENAPI_SOURCE=app`（默认）时工具集与 **`/openapi.json` 全量一致**；`file` / `legacy` 时仅加载 `openai_spec.json` **物化子集**（工具数量会明显变少，可能**没有** `get_nextjs_template`）。子 Agent 须在「全量 MCP」下才能完成「先拉 schema 再填 content」的标准流程。 |

与 MCP 部署、环境变量、代理路径的说明见 **`docs/mcp-openclaw-materialize-reference.md`**。

---

## 1. 角色与职责

| 项目 | 说明 |
|------|------|
| **唯一职责** | 为下游物化准备 **合法的 `template` + 每页 `layout_id` + `content`**；通过 MCP 调用 **`get_nextjs_template`**（或等价工具）拿 schema；可选补充 `outline_summary`、`speaker_note`。 |
| **不负责** | 整稿叙事可交给主 Agent；**不**在 Presenton 侧触发服务端 LLM；导出与写库由 **MCP 物化工具**（如 `materialize_presentation` / 异步任务工具）完成，本子 Agent 负责把请求体做对。 |
| **输出形态** | 结构化数据：合法 `template`、`slides[]`，或可交给主 Agent / 下一工具调用的 **`MaterializePresentationRequest` 兼容 JSON**（与 MCP 工具参数一致）。 |

---

## 2. 物化侧允许的 `template` 值（硬约束）

FastAPI 校验（`utils/template_validation.py` + `constants/presentation.py`）**仅接受**：

- 内置四选一（大小写不敏感时会归一为小写，但建议始终传小写）：`general`、`modern`、`standard`、`swift`
- 用户自定义：`custom-{uuid}`，且该 UUID 必须在 Presenton 数据库 `templates` 表中存在

**禁止**将下列名称直接写入物化请求的 `template` 字段：

- `neo-general`、`neo-modern`、`neo-standard`、`neo-swift`（Next 前端注册中存在这些 **模板组**，但 **当前物化 API 不会接受**，会返回 400 `Template not found`）
- MCP 工具 **`list_nextjs_presentation_templates`**（对应 `GET /api/v1/nextjs/templates`）返回的 **磁盘目录名** 与「可物化的 `template` 字符串」**不是同一概念**；目录里含 `neo-*`，**不能**据此把物化请求里的 `template` 设为 `neo-*`

子 Agent 在说明「可选风格」时，应映射到上述 **四个内置名之一** 或已知的 `custom-{uuid}`。

---

## 3. `layout_id` 与模板组一致性

- 每一页的 `layout_id` 必须出现在 **该 `template` 对应组** 的版式列表里，且与物化请求中的 `template` **前缀一致**。
- Next 中版式 ID 规则（`presentation-templates/utils.ts` 的 `createTemplateEntry`）：  
  `layout_id`（API 中的字符串）= `{templateName}:{componentLayoutId}`  
  例如经典 General 组：`general:general-intro-slide`（具体枚举以接口为准）。
- **禁止**编造 `layout_id`、从其它 `template` 组复制 ID、或混用前缀（例如 `template` 为 `general` 却使用 `modern:...`），否则物化返回 **400**（`layout_id not found in template`）或 **422**（schema 不匹配）。

---

## 4. 标准工作流程（MCP 工具顺序）

以下以 **`PRESENTON_MCP_OPENAPI_SOURCE=app` 全量 OpenAPI** 为前提；工具名以部署实例 MCP **`tools/list`** 为准（OpenClaw allow 多为 `presenton__` 前缀 + 同名）。

1. **（可选）探活**：在 MCP **`tools/list`** 中找到对应 **`/api/v1/healthz`** 的工具并调用（`operationId` 随 OpenAPI 生成规则而定，勿手写猜测）。
2. **拉取版式与 JSON Schema（强建议）**  
   - 调用 MCP：**`get_nextjs_template`**，`group` = 第 2 节合法值（如 `general`）。  
   - 等价 HTTP：`GET /api/v1/nextjs/template?group=…`（仅作排障对照，OpenClaw 侧以 MCP 为准）。  
   - 响应中 `slides[]` 含每页 **`id`（即物化用的 `layout_id`）**、`name`、`json_schema`。
3. **按 Schema 生成 `content`**  
   - 每个 slide 的 `content` 必须满足对应 `json_schema`；服务端校验失败为 **422**，`detail` 常含 `Slide content failed JSON Schema validation`。
4. **物化**  
   - **同步**：MCP 工具 **`materialize_presentation`**（或 OpenAPI 生成的同义 `operationId`）。  
   - **异步**：**`start_materialize_presentation`** + 轮询 **`get_materialize_job`**（子集模式 `openai_spec.json` 中常见命名；全量模式下以 `.../materialize/jobs/{job_id}` 的 `operationId` 为准）。  

**不要**在未调用 **`get_nextjs_template`** 的情况下凭记忆填 `layout_id` / 字段名。若 OpenClaw 仅放行 `file` 子集且无模板工具，须让运维改为 **`PRESENTON_MCP_OPENAPI_SOURCE=app`** 或扩充 `openai_spec.json`，否则本子 Agent 无法可靠履职。

---

## 5. 列举模板 MCP 工具的误用风险

- **`list_nextjs_presentation_templates`** 扫描 Next 工程下 `presentation-templates` **目录**，返回文件夹与文件列表。
- 部署缺失该目录时 MCP 调用可能返回 **500**（运维问题，非模板逻辑）。
- 子 Agent **不得**假设「列表中的每一个 `templateName` 都可用于物化的 `template`」；**唯一可信的物化模板集合**见第 2 节。

---

## 6. `ordered` 与幻灯片顺序

- `get_nextjs_template` 响应中带 `ordered`（来自模板组 `settings`）。
- 若 `ordered: true`，幻灯片顺序应遵循业务上该模板定义的次序意图；否则至少保持 `slides[]` 与最终叙事顺序一致（数组顺序即页码）。

---

## 7. 性能与超时

- **`get_nextjs_template`** 在服务端会触发 Next 的 `/api/template`（headless），**可能很慢**（分钟级）；相关超时见 **`PRESENTON_NEXTJS_HTTP_TIMEOUT`**（默认 300s），MCP 进程侧还有 **`PRESENTON_HTTP_TIMEOUT`**。
- 子 Agent 应 **单次拉取、在同一对话/任务内复用** 返回的 schema，避免对同一 `group` 高频重复调用 MCP。

---

## 8. 与主 Agent 的交接字段（`MaterializePresentationRequest` 摘要）

子 Agent 应确保以下字段就绪（见 `servers/fastapi/models/materialize_presentation_request.py`）：

| 字段 | 约束 |
|------|------|
| `template` | 第 2 节合法值 |
| `slides` | 长度 ≥ 1；每项含 `layout_id`、`content` |
| `export_as` | `pptx` 或 `pdf` |
| `schema_version` | 省略或 `"1.0"` |
| `title` / `outline_summary` | 建议填写便于导出文件名与大纲展示 |
| `presentation_id` | 若指定，必须尚未存在，否则 **409** |

---

## 9. 常见错误码（便于自检）

| HTTP | 含义 | 子 Agent 侧应对 |
|------|------|----------------|
| 400 | 模板名非法、`layout_id` 不属于该模板 | 对照 MCP **`get_nextjs_template`** 返回值修正 `template` / `layout_id` |
| 422 | 请求体字段无效或 **`content` 不符合 `json_schema`** | 按 `detail.errors` 改字段类型/必填项 |
| 502 | Next 不可达或代理失败 | 运维/基址；非模板逻辑能修复 |
| 409 | `presentation_id` 已存在 | 换 UUID 或省略 |

---

## 10. 反模式清单（明确禁止）

1. 使用 `neo-*` 作为 `materialize.template`。
2. 把 `list_nextjs_templates` 的目录名 **不加甄别** 当作物化 `template`。
3. 根据版式「标题」猜测 `layout_id`，而不使用接口返回的 **`id`**。
4. 在 `content` 中使用 Schema 未声明的字段「碰运气」。
5. 将图标名随意拼接而不参考 MCP 提供的 **`/api/v1/ppt/icons/search`** 对应工具（若 Schema 要求图标类字段；全量 OpenAPI 下通常存在）。

---

## 11. 参考文档（仓库内）

- `docs/mcp-openclaw-materialize-reference.md`：**OpenClaw + MCP**、环境变量、代理路径、工具发现方式  
- `docs/external-agent-materialize.md`：物化 HTTP 契约（与 MCP 工具参数一致）  
- `scripts/verify-presenton-mcp-allow.mjs`：对 MCP 做 `tools/list`，与 OpenClaw `presenton__*` allow 对照  
- `servers/fastapi/mcp_server.py`：MCP 进程入口、`PRESENTON_MCP_OPENAPI_SOURCE`  
- `servers/fastapi/constants/presentation.py`：`DEFAULT_TEMPLATES`  
- `servers/nextjs/app/presentation-templates/index.tsx`：各组版式注册与 `getSchemaByTemplateId`

---

*若未来产品允许 `neo-*` 作为物化 `template`，需同步修改 `DEFAULT_TEMPLATES` / `validate_presentation_template_name`；在此之前，本子 Agent 必须以本文第 2 节为准。*
