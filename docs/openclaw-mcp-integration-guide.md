# OpenClaw MCP 集成指南

将 Presenton PPT 生成能力集成到 OpenClaw（或其他 AI Agent）的完整指南。

---

## 一、集成概述

### 1.1 架构关系

```
┌─────────────────┐      MCP 协议       ┌──────────────────┐
│   OpenClaw      │◄──────────────────►│  Presenton MCP   │
│   (AI Agent)    │                     │    Server        │
│                 │                     │                  │
│  - 上下文管理    │                     │  - 模板查询       │
│  - 内容生成      │                     │  - PPT 物化生成   │
│  - 用户交互      │                     │  - 导出服务       │
└─────────────────┘                     └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌──────────────────┐
                                        │  Presenton API   │
                                        │  (FastAPI :5000) │
                                        └──────────────────┘
```

### 1.2 两种集成模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| **模式 A**: MCP Server | 通过 MCP 协议暴露 Presenton API | OpenClaw 支持 MCP 工具发现 |
| **模式 B**: 直接 HTTP | OpenClaw 直接调用 Presenton HTTP API | 简单集成或自定义协议 |

---

## 二、模式 A：通过 MCP Server 集成

### 2.1 启动 Presenton MCP Server

**方式 1: 使用启动脚本（推荐）**

```bash
# 启动 MCP Server（自动处理容器内进程）
./scripts/start-mcp-server.sh
```

**跨主机访问**（MCP 与 Presenton API 不在同一台机器）：
```bash
# 设置环境变量指定 Presenton API 地址
export PRESENTON_API_BASE_URL="http://192.168.3.58:5000"
./scripts/start-mcp-server.sh
```

输出示例：
```
=== Presenton MCP Server Starter ===
1. Stopping existing MCP server (if any)...
2. Starting MCP server on port 8001...
3. Verifying MCP server is running...
SUCCESS: MCP server is running on port 8001

=== Connection Info ===
MCP SSE Endpoint: http://localhost:8001/mcp
Transport: HTTP (SSE)

=== OpenClaw/Cursor Configuration ===
Add to your MCP settings:
{
  "mcpServers": {
    "presenton": {
      "url": "http://localhost:8001/mcp",
      "transport": "http",
      "name": "Presenton PPT Generator"
    }
  }
}
```

**方式 2: 直接运行（开发环境）**

```bash
cd servers/fastapi
python mcp_server.py --port 8001 --name "Presenton"
```

**方式 3: Docker 容器内运行**

```bash
# 在容器内启动 MCP Server
docker exec -d -w /app/servers/fastapi presenton_development_1 \
  python /app/servers/fastapi/mcp_server.py --port 8001 --name "Presenton"
```

**配置参数**:
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--port` | 8001 | MCP Server 监听端口 |
| `--name` | "Presenton API (OpenAPI)" | MCP 服务器名称 |

**端口映射**：
确保 `docker-compose.yml` 中包含 MCP 端口映射：
```yaml
services:
  development:
    ports:
      - "5000:80"      # Presenton Web UI
      - "1455:1455"    # OAuth callback
      - "8001:8001"    # MCP Server
```

### 2.2 OpenClaw MCP 配置

在 OpenClaw 的配置文件中添加 MCP Server:

```json
{
  "mcpServers": {
    "presenton": {
      "url": "http://localhost:8001/mcp",
      "transport": "http",
      "name": "Presenton PPT Generator"
    }
  }
}
```

**跨主机/跨网络配置**：

如果 MCP Server 与 Presenton API 不在同一台机器，需要：

1. 启动 MCP 时设置环境变量：
```bash
export PRESENTON_API_BASE_URL="http://192.168.3.58:5000"
./scripts/start-mcp-server.sh
```

2. 客户端配置使用正确的 MCP 地址：
```json
{
  "mcpServers": {
    "presenton": {
      "url": "http://192.168.3.58:8001/mcp",
      "transport": "http",
      "name": "Presenton PPT Generator"
    }
  }
}
```

**Cursor 配置步骤**：
1. 打开 Cursor Settings → MCP
2. 点击 "Add MCP Server"
3. 填入：
   - Name: `Presenton`
   - URL: `http://localhost:8001/mcp`
   - Transport: `HTTP (SSE)`
4. 保存后应显示为绿色连接状态

**验证连接**：
```bash
# 测试 MCP endpoint
curl http://localhost:8001/mcp \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}'
```

或Claude Code 配置 (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "presenton": {
      "command": "python",
      "args": ["/path/to/presenton/servers/fastapi/mcp_server.py", "--port", "8001"],
      "env": {
        "PRESENTON_API_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

### 2.3 MCP 工具列表

Presenton MCP Server 自动从 OpenAPI 规范暴露以下工具:

| 工具名 | 功能 | 输入参数 |
|--------|------|----------|
| `materialize_presentation` | 生成 PPT（无 LLM） | `template`, `slides`, `export_as` |
| `generate_presentation` | 生成 PPT（服务端 LLM） | `content`, `n_slides`, `template` |
| `templates_list` | 获取模板列表 | 无 |

### 2.4 调用示例（MCP 协议）

```typescript
// OpenClaw 内调用示例
const result = await mcp.callTool('presenton', 'materialize_presentation', {
  template: 'general',
  slides: [
    {
      layout_id: 'general:general-intro-slide',
      content: {
        title: '产品发布会',
        description: '全新一代 AI 办公平台',
        presenterName: '张三',
        presentationDate: '2026-04-13',
        image: {
          __image_url__: 'https://images.unsplash.com/photo-1505373877841-8d43f7d385dc?w=800',
          __image_prompt__: 'Product launch event'
        }
      }
    }
  ],
  export_as: 'pptx',
  language: 'zh-CN'
});

// 返回结果
{
  presentation_id: 'abc-123-xyz',
  path: '/app_data/exports/产品发布会.pptx',
  edit_path: '/presentation?id=abc-123-xyz'
}
```

---

## 三、模式 B：直接 HTTP 集成

### 3.1 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/ppt/presentation/materialize` | POST | 生成 PPT（推荐） |
| `/api/template?group={template}` | GET | 获取模板布局定义 |

### 3.2 完整调用流程

```python
import requests
import json

PRESENTON_API = "http://localhost:8000"

# 步骤 1: 获取模板布局定义
def get_template_layouts(template_name: str) -> dict:
    """获取指定模板的所有布局及其 JSON Schema"""
    response = requests.get(
        f"{PRESENTON_API}/api/template?group={template_name}"
    )
    return response.json()

# 步骤 2: 构建 PPT 内容
def build_presentation():
    # 先获取模板定义，了解可用布局和字段要求
    layouts = get_template_layouts("general")
    print(f"可用布局：{[s['name'] for s in layouts['slides']]}")
    
    # 构建请求体
    return {
        "template": "general",
        "title": "项目进度汇报",
        "language": "zh-CN",
        "export_as": "pptx",
        "slides": [
            {
                "layout_id": "general:general-intro-slide",
                "content": {
                    "title": "项目进度汇报",
                    "description": "2026 年 Q1 季度项目进展总结",
                    "presenterName": "李四",
                    "presentationDate": "2026-04-13",
                    "image": {
                        "__image_url__": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800",
                        "__image_prompt__": "Project team meeting"
                    }
                }
            },
            {
                "layout_id": "general:metrics-slide",
                "content": {
                    "title": "关键指标达成",
                    "metrics": [
                        {
                            "label": "完成率",
                            "value": "95%",
                            "description": "整体项目进度完成 95%"
                        },
                        {
                            "label": "预算使用",
                            "value": "88%",
                            "description": "预算控制在预期范围内"
                        },
                        {
                            "label": "团队规模",
                            "value": "15 人",
                            "description": "核心团队成员 15 人"
                        }
                    ]
                }
            }
        ]
    }

# 步骤 3: 调用生成接口
def generate_ppt(presentation_data: dict):
    response = requests.post(
        f"{PRESENTON_API}/api/v1/ppt/presentation/materialize",
        json=presentation_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"PPT 生成成功!")
        print(f"  Presentation ID: {result['presentation_id']}")
        print(f"  文件路径：{result['path']}")
        print(f"  编辑链接：{result['edit_path']}")
        return result
    else:
        print(f"生成失败：{response.status_code}")
        print(f"错误详情：{response.json()}")
        return None

# 执行
if __name__ == "__main__":
    ppt_data = build_presentation()
    result = generate_ppt(ppt_data)
```

### 3.3 Node.js 调用示例

```javascript
const axios = require('axios');

const PRESENTON_API = 'http://localhost:8000';

async function generatePresentation() {
  try {
    const response = await axios.post(
      `${PRESENTON_API}/api/v1/ppt/presentation/materialize`,
      {
        template: 'modern',
        title: '融资路演',
        language: 'zh-CN',
        export_as: 'pptx',
        slides: [
          {
            layout_id: 'modern:intro-pitchdeck-slide',
            content: {
              title: '智能办公',
              description: 'AI 驱动的企业级办公自动化平台',
              introCard: {
                enabled: true,
                name: '王五 CEO',
                date: '2026 年 4 月'
              },
              image: {
                __image_url__: 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800',
                __image_prompt__: 'Startup pitch deck'
              }
            }
          }
        ]
      }
    );
    
    console.log('PPT 生成成功:', response.data);
    return response.data;
  } catch (error) {
    console.error('生成失败:', error.response?.data || error.message);
    throw error;
  }
}
```

---

## 四、OpenClaw Agent 开发指南

### 4.1 Agent 提示词设计

为 OpenClaw 配置专用提示词，使其理解如何使用 Presenton:

```markdown
## PPT 生成能力说明

你可以通过 Presenton MCP 工具生成专业 PPT 演示文稿。

### 可用模板

| 模板 | 适用场景 | 风格 |
|------|----------|------|
| general | 通用商务、年度报告 | 紫色系，专业稳重 |
| modern | 融资路演、产品介绍 | 蓝色系，现代简洁 |
| standard | 政府汇报、学术演示 | 绿色系，正式传统 |
| swift | 内部会议、快速更新 | 青色系，极简快速 |

### 生成流程

1. **询问需求**: 了解演示场景、受众、核心信息
2. **选择模板**: 根据场景推荐合适模板
3. **规划结构**: 设计 PPT 大纲（封面→目录→内容→总结）
4. **选择布局**: 为每页选择合适的布局
5. **生成内容**: 根据布局 Schema 构建 content 对象
6. **调用工具**: 使用 materialize_presentation 工具生成

### 布局选择指南

- 封面开场 → `general-intro-slide` 或 `intro-pitchdeck-slide`
- 目录索引 → `table-of-contents-slide`
- 数据指标 → `metrics-slide`（大数字展示）
- 要点列举 → `bullet-with-icons-slide`（配图标）
- 数据对比 → `table-info-slide`（表格）
- 团队介绍 → `team-slide`
- 引用强调 → `quote-slide`

### 注意事项

- 标题长度控制在 10-30 字
- 描述文字 50-120 字为宜
- 图片使用 Unsplash 等可靠源
- 严格遵守 JSON Schema 字段长度限制
```

### 4.2 OpenClaw Tool 定义

如果 OpenClaw 支持自定义 Tool，可定义如下:

```typescript
const presentonTools = {
  materialize_presentation: {
    description: '生成 PPT 演示文稿，需要指定模板和每页内容',
    parameters: {
      template: {
        type: 'string',
        enum: ['general', 'modern', 'standard', 'swift'],
        description: 'PPT 模板名称'
      },
      slides: {
        type: 'array',
        description: '幻灯片数组，每页包含 layout_id 和 content',
        items: {
          layout_id: { type: 'string', description: '布局 ID' },
          content: { type: 'object', description: '符合布局 Schema 的内容' }
        }
      },
      export_as: {
        type: 'string',
        enum: ['pptx', 'pdf'],
        default: 'pptx'
      },
      language: {
        type: 'string',
        default: 'zh-CN'
      }
    }
  },
  
  get_template_info: {
    description: '获取指定模板的布局列表和 Schema 定义',
    parameters: {
      template: {
        type: 'string',
        enum: ['general', 'modern', 'standard', 'swift'],
        description: '模板名称'
      }
    }
  }
};
```

### 4.3 多轮对话示例

```
用户：帮我做一份产品发布会的 PPT

Agent: 好的，我来帮您设计产品发布会 PPT。请问：
1. 这是什么类型的产品？（科技/消费/服务等）
2. 发布会规模？（内部/媒体/投资人等）
3. 需要突出哪些核心信息？

用户：是一款 AI 办公软件，面向媒体和投资人，
      想突出技术领先、市场机会、商业模式

Agent: 了解。我建议使用 **modern（现代路演）** 模板，
蓝色系设计适合投资人演示。PPT 结构规划如下：

1. 封面 - 产品定位
2. 市场规模 - TAM/SAM/SOM
3. 痛点分析 - 3 个核心痛点
4. 解决方案 - 产品优势
5. 商业模式 - 收入来源
6. 竞争优势 - 竞品对比
7. 团队介绍 - 核心成员
8. 财务预测 - 关键指标

现在开始生成，请稍候...

[调用 materialize_presentation 工具]

PPT 已生成完成！
- 文件：产品发布会.pptx
- 页数：8 页
- 模板：modern（蓝色系路演风格）
- 下载路径：/app_data/exports/产品发布会.pptx

需要我调整哪一页的内容或设计风格吗？
```

---

## 五、错误处理与调试

### 5.1 常见错误码

| HTTP 状态码 | 原因 | 解决方案 |
|-------------|------|----------|
| 400 | `layout_id` 不存在于模板中 | 检查布局 ID 格式 `模板名：布局名` |
| 400 | `slides` 数组为空 | 至少提供 1 页幻灯片 |
| 422 | JSON Schema 验证失败 | 检查 `content` 字段类型和长度 |
| 422 | 必填字段缺失 | 检查 schema 中 `required` 数组 |
| 502 | Next.js 模板服务不可用 | 重启 Presenton 服务 |
| 500 | 导出失败 | 检查 Puppeteer/Chromium 状态 |

### 5.2 调试技巧

```python
# 1. 先获取模板定义，确认可用布局
layouts = requests.get(f"{API}/api/template?group=general").json()
print("可用布局:", [l['id'] for l in layouts['slides']])

# 2. 打印完整 Schema 用于验证
for layout in layouts['slides']:
    print(f"\n{layout['id']}:")
    print(json.dumps(layout['json_schema'], indent=2))

# 3. 单页测试，成功后再提交完整 PPT
test_payload = {
    "template": "general",
    "slides": [single_slide],  # 先测试单页
    "export_as": "pptx"
}
response = requests.post(f"{API}/api/v1/ppt/presentation/materialize", json=test_payload)
print(response.json())

# 4. 详细错误解析
if response.status_code == 422:
    errors = response.json().get('detail', [])
    for err in errors:
        print(f"字段：{err.get('loc')}, 错误：{err.get('msg')}")
```

### 5.3 日志级别配置

在 `mcp_server.py` 中添加调试日志:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("presenton-mcp")

# 在关键位置添加日志
logger.debug(f"收到请求：{request_body}")
logger.info(f"模板验证通过：{template_name}")
logger.error(f"Schema 验证失败：{errors}")
```

---

## 六、高级用法

### 6.1 批量生成

```python
def batch_generate_presentations(topics: list):
    """批量生成多个主题的 PPT"""
    results = []
    for topic in topics:
        ppt_data = build_presentation_for_topic(topic)
        result = generate_ppt(ppt_data)
        results.append({
            'topic': topic,
            'presentation_id': result['presentation_id'],
            'path': result['path']
        })
    return results

# 使用
topics = ['产品发布', '融资路演', '季度汇报', '客户案例']
batch_generate_presentations(topics)
```

### 6.2 模板混用

```python
# 根据内容类型动态选择模板
def select_template_by_content(content_type: str) -> str:
    template_map = {
        'pitch_deck': 'modern',
        'annual_report': 'general',
        'board_meeting': 'standard',
        'weekly_update': 'swift'
    }
    return template_map.get(content_type, 'general')
```

### 6.3 内容复用

```python
def clone_presentation(source_id: str, modifications: dict):
    """基于现有 PPT 创建新版本"""
    # 1. 获取原始 PPT 数据
    source = requests.get(f"{API}/api/v1/ppt/presentation/{source_id}").json()
    
    # 2. 应用修改
    modified_slides = apply_modifications(source['slides'], modifications)
    
    # 3. 重新生成
    return generate_ppt({
        'template': source['template']['name'],
        'slides': modified_slides,
        'export_as': 'pptx'
    })
```

---

## 七、部署配置

### 7.1 开发环境

```bash
# 1. 启动 Presenton 服务
docker compose up development

# 2. 启动 MCP Server
python servers/fastapi/mcp_server.py --port 8001

# 3. 验证服务
curl http://localhost:8000/api/v1/ppt/presentation/materialize -X OPTIONS
curl http://localhost:8001/sse
```

### 7.2 生产环境

```yaml
# docker-compose.prod.yml
services:
  presenton-api:
    image: presenton:latest
    ports:
      - "8000:80"
    environment:
      - DATABASE_URL=postgresql://...
      - OPENAI_API_KEY=sk-...
  
  presenton-mcp:
    image: presenton:latest
    command: python /app/servers/fastapi/mcp_server.py --port 8001
    environment:
      - PRESENTON_API_BASE_URL=http://presenton-api:8000
    ports:
      - "8001:8001"
    depends_on:
      - presenton-api
```

### 7.3 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PRESENTON_API_BASE_URL` | `http://127.0.0.1:8000` | Presenton API 地址 |
| `MCP_SERVER_PORT` | `8001` | MCP Server 端口 |
| `MCP_SERVER_NAME` | `Presenton API (OpenAPI)` | MCP 服务器名称 |

---

## 八、最佳实践

### 8.1 内容设计原则

1. **一页一焦点**: 每页只传达一个核心信息
2. **数据可视化**: 优先使用 metrics/chart 布局展示数字
3. **图文配合**: 每页配图与内容主题相关
4. **简洁文字**: 标题<30 字，描述<120 字，要点<80 字

### 8.2 布局选择决策树

```
内容类型？
├─ 封面/标题 → intro-slide / intro-pitchdeck-slide
├─ 目录 → table-of-contents-slide
├─ 大数字指标 → metrics-slide
├─ 带图指标 → metrics-with-image-slide
├─ 要点 (有图标) → bullet-with-icons-slide
├─ 要点 (有顺序) → numbered-bullets-slide
├─ 数据对比 → table-info-slide
├─ 趋势分析 → chart-with-bullets-slide
├─ 团队介绍 → team-slide
├─ 引用/评价 → quote-slide
└─ 联系方式 → contact-layout (standard)
```

### 8.3 图片资源推荐

```javascript
// 推荐图片源（免费、高质量、可直接使用）
const imageSources = {
  unsplash: 'https://images.unsplash.com/photo-{ID}?w=800&q=80',
  pexels: 'https://images.pexels.com/photos/{ID}/pexels-photo-{ID}.jpeg',
  
  // 主题关键词参考
  business: ['meeting', 'presentation', 'office', 'teamwork'],
  technology: ['ai', 'software', 'digital', 'innovation'],
  finance: ['chart', 'graph', 'growth', 'investment']
};
```

---

## 附录 A：完整布局 ID 参考

### General (12 种)
```
general:general-intro-slide
general:basic-info-slide
general:bullet-icons-only-slide
general:bullet-with-icons-slide
general:chart-with-bullets-slide
general:metrics-slide
general:metrics-with-image-slide
general:numbered-bullets-slide
general:quote-slide
general:table-info-slide
general:table-of-contents-slide
general:team-slide
```

### Modern (10 种)
```
modern:intro-pitchdeck-slide
modern:bullets-with-icons-description-grid
modern:bullet-with-icons-slide
modern:chart-or-table-with-description
modern:chart-or-table-with-metrics-description
modern:image-and-description
modern:image-list-with-description
modern:images-with-description
modern:metrics-with-description
modern:table-of-contents
```

### Standard (11 种)
```
standard:header-counter-two-column-image-text-slide
standard:chart-left-text-right
standard:contact
standard:heading-bullet-image-description
standard:icon-bullet-description
standard:icon-image-description
standard:image-list-with-description
standard:metrics-description
standard:numbered-bullet-single-image
standard:table-of-contents
standard:visual-metrics
```

### Swift (9 种)
```
swift:IntroSlideLayout
swift:BulletsWithIconsTitleDescription
swift:IconBulletListDescription
swift:ImageListDescription
swift:MetricsNumbers
swift:SimpleBulletPointsLayout
swift:TableOfContents
swift:TableorChart
swift:Timeline
```

---

## 附录 B：相关文档

- [Presentation MCP Skills](./presentation-mcp-skills.md) - 完整布局目录和 Schema 说明
- [External Agent Materialize](./external-agent-materialize.md) - 物化接口设计文档
- [Docker Compose 环境说明](./docker-compose-environments.md) - 部署配置
- [部署架构说明](./deployment-architecture.md) - 系统架构
