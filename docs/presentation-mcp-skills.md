# Presenton Presentation MCP Skills

通过 MCP 协议使用 Presenton 生成专业 PPT 的完整指南。

---

## 快速开始

### 基本调用结构

```json
POST /api/v1/ppt/presentation/materialize
{
  "template": "general",
  "slides": [...],
  "export_as": "pptx",
  "language": "zh-CN"
}
```

---

## 一、模板选择指南

### 1.1 模板清单

| 模板名称 | 布局数量 | 字体 | 配色 | 适用场景 |
|----------|----------|------|------|----------|
| `general` | 12 | Poppins | 紫色系 #9333ea | 通用商务、年度报告 |
| `modern` | 10 | Montserrat | 蓝色系 #1E4CD9 | 融资路演、投资人演示 |
| `standard` | 11 | Playfair Display | 绿色系 #1B8C2D | 政府汇报、学术演示 |
| `swift` | 9 | Albert Sans | 青色系 #BFF4FF | 站立会议、快速更新 |

### 1.2 按场景选择模板

```python
# 融资路演 → modern
# 年度报告 → general
# 董事会汇报 → standard
# 内部周会 → swift
# 数据分析 → general (metrics 布局丰富)
# 产品介绍 → modern (视觉吸引力强)
```

---

## 二、布局详细目录

### 2.1 General 模板布局（12 种）

#### `general:general-intro-slide` - 封面页
**用途**: 演示文稿首页，包含标题、描述、演讲者信息
**特点**: 左图右文布局，紫色圆形头像背景，优雅专业

| 字段 | 类型 | 长度 | 必填 | 说明 |
|------|------|------|------|------|
| title | string | 3-40 | 是 | 主标题 |
| description | string | 10-150 | 是 | 副标题/描述 |
| presenterName | string | 2-50 | 是 | 演讲者姓名 |
| presentationDate | string | 2-50 | 是 | 日期 (如 2026-04-13) |
| image.__image_url__ | URL | - | 是 | 图片 URL |
| image.__image_prompt__ | string | 10-50 | 是 | 图片描述提示词 |

**示例**:
```json
{
  "layout_id": "general:general-intro-slide",
  "content": {
    "title": "产品发布会",
    "description": "全新一代智能办公解决方案",
    "presenterName": "张三",
    "presentationDate": "2026-04-13",
    "image": {
      "__image_url__": "https://images.unsplash.com/photo-1505373877841-8d43f7d385dc?w=800",
      "__image_prompt__": "Professional product launch event"
    }
  }
}
```

---

#### `general:basic-info-slide` - 基础信息页
**用途**: 单主题介绍，配合图说明
**特点**: 简洁的左文右图布局

| 字段 | 类型 | 长度 | 必填 |
|------|------|------|------|
| title | string | 3-40 | 是 |
| description | string | 10-150 | 是 |
| image | ImageObject | - | 是 |

---

#### `general:bullet-with-icons-slide` - 图标要点页 ⭐高频
**用途**: 多要点列举，每个要点配图标
**特点**: 左图右文，3 个图标要点卡片

| 字段 | 类型 | 长度 | 必填 | 说明 |
|------|------|------|------|------|
| title | string | 3-40 | 是 | 标题 |
| description | string | 10-150 | 是 | 描述 |
| image | ImageObject | - | 是 | 配图 |
| bulletPoints | Array | 1-3 | 是 | 要点列表 |
| bulletPoints[].title | string | 2-60 | 是 | 要点标题 |
| bulletPoints[].description | string | 10-100 | 是 | 要点描述 |
| bulletPoints[].icon.__icon_url__ | URL | - | 是 | 图标 URL |
| bulletPoints[].icon.__icon_query__ | string | 5-20 | 是 | 图标搜索词 |

**示例**:
```json
{
  "layout_id": "general:bullet-with-icons-slide",
  "content": {
    "title": "核心优势",
    "description": "我们的产品具有三大核心优势",
    "image": {
      "__image_url__": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800",
      "__image_prompt__": "Business team collaboration"
    },
    "bulletPoints": [
      {
        "title": "高效便捷",
        "description": "自动化工作流提升 300% 效率",
        "icon": {
          "__icon_url__": "https://presenton-public.s3.ap-southeast-1.amazonaws.com/static/icons/bold/lightning-bold.svg",
          "__icon_query__": "fast efficiency"
        }
      },
      {
        "title": "安全可靠",
        "description": "企业级安全保护您的数据",
        "icon": {
          "__icon_url__": "https://presenton-public.s3.ap-southeast-1.amazonaws.com/static/icons/bold/shield-bold.svg",
          "__icon_query__": "security protection"
        }
      },
      {
        "title": "灵活扩展",
        "description": "按需扩展满足业务增长",
        "icon": {
          "__icon_url__": "https://presenton-public.s3.ap-southeast-1.amazonaws.com/static/icons/bold/chart-bold.svg",
          "__icon_query__": "growth scalable"
        }
      }
    ]
  }
}
```

---

#### `general:metrics-slide` - 数据指标页 ⭐高频
**用途**: 展示关键业务指标、数据统计
**特点**: 大数字 + 标签 + 描述框，视觉冲击力强

| 字段 | 类型 | 长度 | 必填 |
|------|------|------|------|
| title | string | 3-100 | 是 |
| metrics | Array(2-3) | - | 是 |
| metrics[].label | string | 2-50 | 是 | 指标标签 |
| metrics[].value | string | 1-10 | 是 | 指标值 (如 150+, 95%) |
| metrics[].description | string | 10-150 | 是 | 指标说明 |

**示例**:
```json
{
  "layout_id": "general:metrics-slide",
  "content": {
    "title": "公司里程碑",
    "metrics": [
      {
        "label": "服务客户",
        "value": "500+",
        "description": "覆盖全球 30 多个国家和地区的企业客户"
      },
      {
        "label": "项目交付",
        "value": "1200+",
        "description": "成功交付超过 1200 个企业级项目"
      },
      {
        "label": "客户满意度",
        "value": "98%",
        "description": "持续保持 98% 以上的客户满意度"
      }
    ]
  }
}
```

---

#### `general:table-of-contents-slide` - 目录页
**用途**: 演示文稿目录，放在封面之后
**特点**: 编号列表，带页码引用

| 字段 | 类型 | 必填 |
|------|------|------|
| sections | Array | 是 |
| sections[].number | number | 是 | 章节号 |
| sections[].title | string (1-80) | 是 | 章节标题 |
| sections[].pageNumber | string | 是 | 页码 |

**示例**:
```json
{
  "layout_id": "general:table-of-contents-slide",
  "content": {
    "sections": [
      {"number": 1, "title": "市场概况", "pageNumber": "03"},
      {"number": 2, "title": "产品介绍", "pageNumber": "05"},
      {"number": 3, "title": "商业模式", "pageNumber": "08"},
      {"number": 4, "title": "财务预测", "pageNumber": "12"}
    ]
  }
}
```

---

#### `general:table-info-slide` - 表格页
**用途**: 数据对比、详细列表
**特点**: 标准表格结构，带表头和描述

| 字段 | 类型 | 必填 |
|------|------|------|
| title | string (3-40) | 是 |
| tableData.headers | Array(2-5) | 是 | 表头 |
| tableData.rows | Array(2-6) | 是 | 数据行 |
| description | string (10-200) | 是 | 表格说明 |

**示例**:
```json
{
  "layout_id": "general:table-info-slide",
  "content": {
    "title": "竞品对比分析",
    "description": "与主要竞争对手的功能对比",
    "tableData": {
      "headers": ["功能", "我们的产品", "竞品 A", "竞品 B"],
      "rows": [
        ["AI 生成", "支持", "不支持", "部分支持"],
        ["多模板", "119 种", "50 种", "30 种"],
        ["导出格式", "PPTX/PDF", "PPTX", "PPTX"]
      ]
    }
  }
}
```

---

#### `general:team-slide` - 团队页
**用途**: 介绍团队成员
**特点**: 2-4 人卡片布局，带头像和简介

| 字段 | 类型 | 必填 |
|------|------|------|
| title | string | 是 |
| companyDescription | string (10-150) | 是 |
| teamMembers | Array(2-4) | 是 |
| teamMembers[].name | string (2-50) | 是 |
| teamMembers[].position | string (2-50) | 是 |
| teamMembers[].description | string (max150) | 是 |
| teamMembers[].image | ImageObject | 是 |

---

#### `general:quote-slide` - 引用页
**用途**: 名言引用、客户评价、核心观点强调
**特点**: 大图背景，文字叠加

| 字段 | 类型 | 长度 | 必填 |
|------|------|------|------|
| heading | string | 3-60 | 是 |
| quote | string | 10-200 | 是 |
| author | string | 2-50 | 是 |
| backgroundImage | ImageObject | - | 是 |

---

#### `general:chart-with-bullets-slide` - 图表要点页
**用途**: 左侧图表 + 右侧要点说明
**特点**: 数据可视化配合文字解释

| 字段 | 类型 | 必填 |
|------|------|------|
| title | string | 是 |
| description | string | 是 |
| chartData | ChartObject | 是 |
| bulletPoints | Array(1-3) | 是 |

---

#### `general:numbered-bullets-slide` - 编号列表页
**用途**: 有序步骤、流程说明
**特点**: 带序号的要点列表

| 字段 | 类型 | 必填 |
|------|------|------|
| title | string | 是 |
| image | ImageObject | 是 |
| bulletPoints | Array(1-3) | 是 |
| bulletPoints[].title | string | 是 |
| bulletPoints[].description | string | 是 |

---

#### `general:metrics-with-image-slide` - 指标配图页
**用途**: 指标数据配合场景图
**特点**: 左图右指标布局

| 字段 | 类型 | 必填 |
|------|------|------|
| title | string | 是 |
| description | string | 是 |
| image | ImageObject | 是 |
| metrics | Array(1-3) | 是 |
| metrics[].label | string | 是 |
| metrics[].value | string | 是 |

---

#### `general:bullet-icons-only-slide` - 纯图标要点页
**用途**: 简洁的图标 + 标题布局
**特点**: 无描述文字，更简洁

---

### 2.2 Modern 模板布局（10 种）

#### `modern:intro-pitchdeck-slide` - 路演封面 ⭐
**用途**: 融资路演首页
**特点**: 大标题，右侧配图，公司信息卡片

| 字段 | 类型 | 长度 | 必填 |
|------|------|------|------|
| title | string | 2-15 | 是 |
| description | string | 1-200 | 是 |
| introCard.enabled | boolean | - | 是 |
| introCard.name | string | 1-60 | 是 |
| introCard.date | string | 1-60 | 是 |
| image | ImageObject | - | 是 |

---

#### `modern:metrics-with-description-image` - 市场规模页
**用途**: TAM/SAM/SOM 市场数据分析
**特点**: 左图右指标，带详细描述

| 字段 | 类型 | 必填 |
|------|------|------|
| title | string | 是 |
| mapImage | ImageObject | 是 |
| marketStats | Array(1-4) | 是 |
| marketStats[].label | string | 是 |
| marketStats[].value | string | 是 |
| marketStats[].description | string | 是 |
| description | string | 是 |

---

### 2.3 Standard 模板布局（11 种）

#### `standard:header-counter-two-column-image-text-slide` - 标准封面
**用途**: 正式文档封面
**特点**: 顶部计数器，左图右文，正式风格

---

### 2.4 Swift 模板布局（9 种）

#### `swift:IntroSlideLayout` - 极简封面
**用途**: 快速演示开场
**特点**: 简洁设计，副标题可配置

---

## 三、Materialize API 完整结构

### 3.1 请求体结构

```typescript
interface MaterializePresentationRequest {
  // 可选：API 版本，使用 1.0 或省略
  schema_version?: "1.0";
  
  // 必填：模板名称
  template: "general" | "modern" | "standard" | "swift";
  
  // 必填：幻灯片数组（至少 1 张）
  slides: MaterializeSlideItem[];
  
  // 必填：导出格式
  export_as: "pptx" | "pdf";
  
  // 必填：语言
  language: string; // 如 "zh-CN", "English"
  
  // 可选：演示文稿标题（不填则自动生成）
  title?: string;
  
  // 可选：演示文稿 ID（用于创建新版本）
  presentation_id?: UUID;
  
  // 可选：内容摘要（用于审计/UI 显示）
  content?: string;
  
  // 可选：生成指令
  instructions?: string;
  
  // 可选：语气风格
  tone?: "DEFAULT" | "FORMAL" | "CASUAL" | "ENTHUSIASTIC";
  
  // 可选：详细程度
  verbosity?: "STANDARD" | "BRIEF" | "DETAILED";
  
  // 可选：主题配置
  theme?: {
    primaryColor?: string;
    backgroundColor?: string;
    // ... 其他主题变量
  };
}

interface MaterializeSlideItem {
  // 必填：布局 ID（格式：模板名：布局名）
  layout_id: string;
  
  // 必填：内容对象（需符合该布局的 JSON Schema）
  content: Record<string, any>;
  
  // 可选：大纲摘要
  outline_summary?: string;
  
  // 可选：演讲者备注
  speaker_note?: string;
  
  // 可选：HTML 内容
  html_content?: string;
  
  // 可选：额外属性
  properties?: Record<string, any>;
}
```

### 3.2 响应体结构

```typescript
interface MaterializePresentationResponse {
  // 演示文稿 ID
  presentation_id: string;
  
  // PPTX/PDF文件路径
  path: string;
  
  // 编辑页面路径
  edit_path: string;
}
```

### 3.3 错误响应

```typescript
interface ErrorResponse {
  detail: {
    message: string;
    layout_id?: string;
    errors?: Array<{
      path: string;
      message: string;
    }>;
  };
}
```

---

## 四、最佳实践

### 4.1 内容长度控制

| 字段类型 | 建议长度 | 注意事项 |
|----------|----------|----------|
| 标题 | 10-30 字 | 简洁有力 |
| 描述 | 50-120 字 | 1-2 句话 |
| 要点描述 | 20-80 字 | 单句表达 |
| 指标说明 | 15-50 字 | 解释数据含义 |

### 4.2 图片选择

```json
{
  "image": {
    "__image_url__": "https://images.unsplash.com/photo-{ID}?w=800&q=80",
    "__image_prompt__": "Business team meeting in modern office"
  }
}
```

**推荐图片源**:
- Unsplash: `https://images.unsplash.com/photo-{ID}`
- 避免使用需要登录的图片源

### 4.3 图标选择

```json
{
  "icon": {
    "__icon_url__": "https://presenton-public.s3.ap-southeast-1.amazonaws.com/static/icons/bold/{name}-bold.svg",
    "__icon_query__": "business meeting"
  }
}
```

**可用图标**: lightning, shield, chart, users, document, briefcase, building, palette, text 等

### 4.4 常见 Schema 验证错误

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `'xxx' is too short` | 字符串长度不足 | 增加描述长度到最小值以上 |
| `'xxx' is too long` | 字符串超出限制 | 精简文字到最大值以内 |
| `layout_id not found` | 布局 ID 错误 | 使用 `模板名：布局名` 格式 |
| `required field missing` | 缺少必填字段 | 检查 schema 中 required 数组 |

---

## 五、完整示例

### 5.1 融资路演 PPT（Modern 模板）

```json
{
  "template": "modern",
  "title": "智能办公解决方案融资路演",
  "language": "zh-CN",
  "export_as": "pptx",
  "slides": [
    {
      "layout_id": "modern:intro-pitchdeck-slide",
      "content": {
        "title": "智能办公",
        "description": "AI 驱动的企业级办公自动化平台",
        "introCard": {
          "enabled": true,
          "name": "李明 CEO",
          "date": "2026 年 4 月"
        },
        "image": {
          "__image_url__": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800",
          "__image_prompt__": "Modern office technology"
        }
      }
    },
    {
      "layout_id": "modern:metrics-with-description-image",
      "content": {
        "title": "市场规模",
        "mapImage": {
          "__image_url__": "https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg",
          "__image_prompt__": "World map with business highlights"
        },
        "marketStats": [
          {
            "label": "TAM 总市场",
            "value": "5000 亿元",
            "description": "全球企业办公软件市场总规模"
          },
          {
            "label": "SAM 可服务市场",
            "value": "800 亿元",
            "description": "亚太地区中小企业市场"
          },
          {
            "label": "SOM 可获得市场",
            "value": "50 亿元",
            "description": "3 年内目标市场份额"
          }
        ],
        "description": "企业数字化转型加速，智能办公市场持续增长"
      }
    }
  ]
}
```

### 5.2 年度报告 PPT（General 模板）

```json
{
  "template": "general",
  "title": "2025 年度业务报告",
  "language": "zh-CN",
  "export_as": "pptx",
  "slides": [
    {
      "layout_id": "general:general-intro-slide",
      "content": {
        "title": "2025 年度业务报告",
        "description": "回顾过去一年的成就与挑战，展望未来发展",
        "presenterName": "王总 总经理",
        "presentationDate": "2026 年 1 月",
        "image": {
          "__image_url__": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800",
          "__image_prompt__": "Business annual report meeting"
        }
      }
    },
    {
      "layout_id": "general:metrics-slide",
      "content": {
        "title": "年度业绩亮点",
        "metrics": [
          {
            "label": "营业收入",
            "value": "2.5 亿",
            "description": "同比增长 45%，超额完成年度目标"
          },
          {
            "label": "新增客户",
            "value": "380 家",
            "description": "覆盖金融、制造、零售等多个行业"
          },
          {
            "label": "客户留存",
            "value": "96%",
            "description": "行业领先的客户满意度和续费率"
          }
        ]
      }
    },
    {
      "layout_id": "general:bullet-with-icons-slide",
      "content": {
        "title": "核心竞争力",
        "description": "持续投入研发，构建技术壁垒",
        "image": {
          "__image_url__": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
          "__image_prompt__": "Technology innovation"
        },
        "bulletPoints": [
          {
            "title": "AI 技术领先",
            "description": "自研大模型，准确率行业第一",
            "icon": {
              "__icon_url__": "https://presenton-public.s3.ap-southeast-1.amazonaws.com/static/icons/bold/lightning-bold.svg",
              "__icon_query__": "AI technology"
            }
          },
          {
            "title": "安全合规",
            "description": "通过 ISO27001 等多项认证",
            "icon": {
              "__icon_url__": "https://presenton-public.s3.ap-southeast-1.amazonaws.com/static/icons/bold/shield-bold.svg",
              "__icon_query__": "security compliance"
            }
          },
          {
            "title": "生态合作",
            "description": "与 50+ 合作伙伴深度整合",
            "icon": {
              "__icon_url__": "https://presenton-public.s3.ap-southeast-1.amazonaws.com/static/icons/bold/users-bold.svg",
              "__icon_query__": "partnership"
            }
          }
        ]
      }
    },
    {
      "layout_id": "general:table-info-slide",
      "content": {
        "title": "财务数据对比",
        "description": "2024-2025 年主要财务指标对比",
        "tableData": {
          "headers": ["指标", "2024 年", "2025 年", "增长率"],
          "rows": [
            ["营业收入", "1.7 亿", "2.5 亿", "45%"],
            ["净利润", "3500 万", "5200 万", "49%"],
            ["研发投入", "4000 万", "6000 万", "50%"],
            ["员工人数", "180", "260", "44%"]
          ]
        }
      }
    },
    {
      "layout_id": "general:quote-slide",
      "content": {
        "heading": "展望未来",
        "quote": "我们的目标是在 2027 年成为亚太地区智能办公市场的领导者，为 10000 家企业提供更高效的工作方式。",
        "author": "李明 董事长",
        "backgroundImage": {
          "__image_url__": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800",
          "__image_prompt__": "Future vision business growth"
        }
      }
    }
  ]
}
```

---

## 六、Agent 创作提示

### 6.1 内容生成原则

1. **先选模板**：根据演示场景选择合适的模板
2. **规划结构**：封面→目录→内容页→总结
3. **匹配布局**：根据内容类型选择布局
   - 数据指标 → metrics-slide
   - 要点列举 → bullet-with-icons-slide
   - 数据对比 → table-info-slide
   - 团队介绍 → team-slide
4. **控制长度**：严格遵守 schema 长度限制
5. **添加图片**：每个布局尽量配图增强视觉效果

### 6.2 布局选择决策树

```
需要展示什么内容？
├─ 封面开场 → intro-slide / intro-pitchdeck-slide
├─ 目录索引 → table-of-contents-slide
├─ 数据指标 → metrics-slide（大数字）
│           └─ metrics-with-image（配场景图）
├─ 要点列举 → bullet-with-icons-slide（有图标）
│           └─ numbered-bullets-slide（有顺序）
├─ 数据对比 → table-info-slide
├─ 趋势分析 → chart-with-bullets-slide
├─ 团队介绍 → team-slide
├─ 引用强调 → quote-slide
└─ 结束页 → quote-slide / intro-slide（复用）
```

### 6.3 高质量 PPT 特征

- [ ] 封面有吸引人的标题和配图
- [ ] 目录清晰列出主要章节
- [ ] 每页有明确的视觉焦点
- [ ] 数据用大数字突出显示
- [ ] 要点配相关图标增强理解
- [ ] 文字简洁，每句不超 2 行
- [ ] 图片与内容主题相关
- [ ] 整体风格统一（不混用模板）

---

## 七、故障排查

### 7.1 常见错误及解决

| 错误 | 可能原因 | 解决方法 |
|------|----------|----------|
| 404 Not Found | 布局 ID 错误 | 检查格式 `模板名：布局名` |
| Schema 验证失败 | 字段长度不符 | 检查 minLength/maxLength |
| 图片加载失败 | URL 无效 | 使用可靠图片源如 Unsplash |
| 导出失败 | 服务器繁忙 | 重试或检查服务器状态 |

### 7.2 调试技巧

1. **验证布局 ID**: 先调用 `/api/template?group={模板名}` 获取有效布局列表
2. **测试单页**: 先提交单页测试，成功后再提交完整 PPT
3. **检查 Schema**: 对比 content 字段与布局的 json_schema
4. **查看错误详情**: 错误响应中 errors 数组包含具体验证失败信息

---

## 附录：完整布局 ID 列表

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
