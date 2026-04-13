# PPT 模板组分析报告

本文档详细分析了 Presenton 项目中 8 套内置 PPT 模板组的特点、设计风格、布局类型和适用场景。

---

## 概述

本项目共有 **8 套模板组**，分为 4 个主要系列（General、Modern、Standard、Swift），每个系列都有 "Neo" 变体和普通变体：

| 模板组 | 布局数量 | 字体 | 主要配色 | 默认模板 |
|--------|----------|------|----------|----------|
| General | 12 | Poppins | 紫色系 (#9333ea) | 是 |
| Neo General | 27 | Poppins | 紫色系 (#9234EB) | 否 |
| Modern | 10 | Montserrat | 蓝色系 (#1E4CD9) | 否 |
| Neo Modern | 17 | Montserrat | 蓝色系 (#002BB2) | 否 |
| Standard | 11 | Playfair Display | 绿色系 (#1B8C2D) | 否 |
| Neo Standard | 17 | Playfair Display | 绿色系 (#1F8A2E) | 否 |
| Swift | 9 | Albert Sans | 青色系 (#BFF4FF) | 否 |
| Neo Swift | 16 | Albert Sans | 青色系 (#9CE0EE) | 否 |

---

## 1. General（通用模板系列）

### 1.1 General（普通版）
**定位**：通用型商务演示模板，适合各类企业演示场景

**设计风格**：
- 字体：Poppins（现代无衬线字体）
- 配色：紫色系主题 (#9333ea)，传达专业与创新
- 特点：简洁大方，装饰元素适度（波浪纹、紫色 accent 线条）

**核心布局**（12 种）：
| 布局名称 | 用途 | 特点 |
|----------|------|------|
| Intro Slide | 封面页 | 左图右文，演讲者信息卡片，紫色圆形头像背景 |
| Basic Info | 基础信息页 | 纯文本信息展示 |
| Bullet Icons Only | 图标列表页 | 仅图标 + 要点，无额外装饰 |
| Bullet With Icons | 图标要点页 | 图标配合要点说明 |
| Chart With Bullets | 图表要点页 | 左侧图表 + 右侧要点列表 |
| Metrics | 数据指标页 | 3 列指标展示，大数字 + 描述框 |
| Metrics With Image | 指标配图页 | 指标配合场景图片 |
| Numbered Bullets | 编号列表页 | 带序号的要点列表 |
| Quote | 引用页 | 大字号引用文本 + 来源信息 |
| Table Info | 表格信息页 | 数据表格展示 |
| Table Of Contents | 目录页 | 章节列表 |
| Team | 团队页 | 团队成员展示 |

**适用场景**：
- 企业年度报告
- 项目汇报
- 产品介绍
- 通用商务演示

---

### 1.2 Neo General（新版通用）
**定位**：现代风格增强版通用模板，视觉层次更丰富

**设计风格**：
- 字体：Poppins
- 配色：紫色系 (#9234EB)，更鲜艳的现代紫
- 特点：强调数据可视化，多图表组合布局

**特色布局**（27 种）：
| 布局名称 | 用途 | 特点 |
|----------|------|------|
| Headline Text With Bullets And Stats | 标题 + 统计 | 左文右数据，3 列垂直指标 |
| Headline Description With Image | 标题描述配图 | 双栏布局，左文右圆角图片 |
| Headline Description With Double Image | 双图布局 | 两张并排图片 + 描述 |
| Indexed Three Column List | 三列索引列表 | 三列等分内容 |
| Text Block With Metric Cards | 文本 + 指标卡片 | 文本块配合指标卡片组 |
| Left Align Quotes | 左对齐引用 | 引用文本靠左展示 |
| Title Description With Table | 标题描述 + 表格 | 标题 + 表格数据 |
| Challenge And Outcome With One Stat | 挑战与成果 | 单指标强调对比 |
| Grid Based Eight Metrics Snapshots | 八指标网格 | 4x2 网格指标展示 |
| Timeline | 时间轴 | 水平时间线布局 |
| Multi-Chart Grid | 多图表网格 | 2x2 或 3x2 图表组合 |
| Title Metrics With Chart | 标题指标 + 图表 | 顶部标题 + 指标 + 主图表 |

**适用场景**：
- 数据驱动型演示
- 高管汇报
- 战略规划
- 业绩展示

---

## 2. Modern（现代模板系列）

### 2.1 Modern（普通版）
**定位**：现代商务路演模板，专业且视觉吸引力强

**设计风格**：
- 字体：Montserrat（几何无衬线字体）
- 配色：蓝白色系 (#1E4CD9)，传达信任与专业
- 特点：留白充足，视觉层次清晰，适合融资路演

**核心布局**（10 种）：
| 布局名称 | 用途 | 特点 |
|----------|------|------|
| Intro Pitch Deck Slide | 路演封面 | 大标题 + 公司信息卡片，右侧配图 |
| Bullets With Icons Description Grid | 图标网格 | 2x2 或 3x2 图标 + 描述网格 |
| Bullet With Icons Slide | 图标要点 | 水平排列图标要点 |
| Chart Or Table With Description | 图表 + 描述 | 左图表右说明 |
| Chart Or Table With Metrics Description | 图表 + 指标 | 图表配合指标说明 |
| Image And Description | 图片描述 | 全宽背景图 + 文字叠加 |
| Image List With Description | 图片列表 | 多图片 + 对应描述 |
| Images With Description | 多图描述 | 网格图片组 + 整体描述 |
| Metrics With Description | 指标描述 | 指标数值 + 详细说明 |
| Table Of Contents | 目录 | 章节列表 + 页码 |

**适用场景**：
- 融资路演 (Pitch Deck)
- 投资人演示
- 创业公司展示
- 产品发布会

---

### 2.2 Neo Modern（新版现代）
**定位**：增强版现代模板，更多数据可视化和对比布局

**设计风格**：
- 字体：Montserrat
- 配色：深蓝色系 (#002BB2)，更沉稳的商务蓝
- 特点：强调对比和趋势展示，丰富的图表类型

**特色布局**（17 种）：
| 布局名称 | 用途 | 特点 |
|----------|------|------|
| Title Description Bullet List | 标题描述列表 | 左标题描述 + 右 bullet 卡片列表 |
| Title Description Contact List | 联系列表 | 联系人信息网格 |
| Title Description Dual Metrics Grid | 双指标网格 | 2x2 指标对比 |
| Title Description Icon Timeline | 图标时间轴 | 带图标的时间线 |
| Title Description Image Right | 右图布局 | 标准左文右图 |
| Title Description Metrics Chart | 指标图表 | 指标 + 图表组合 |
| Title Dual Comparison Charts | 双图表对比 | 左右两个图表对比 |
| Title Dual Comparison Cards | 双卡片对比 | 左右对比卡片 |
| Title Horizontal Alternating Timeline | 交替时间轴 | 上下交替时间线 |
| Title KPI Snapshot Grid | KPI 快照 | 多指标 KPI 网格 |
| Title Subtitles Chart | 副标题图表 | 多副标题 + 主图表 |
| Title Description Multi-Chart Grid | 多图表网格 | 2x2/3x2 图表组合 |

**适用场景**：
- 数据分析报告
- 市场趋势分析
- 竞争对手对比
- 年度业绩回顾

---

## 3. Standard（标准模板系列）

### 3.1 Standard（普通版）
**定位**：经典稳重的商务模板，适合正式场合

**设计风格**：
- 字体：Playfair Display（优雅衬线字体）
- 配色：绿色系 (#1B8C2D)，传达成长与稳定
- 特点：传统商务风格，正式感强

**核心布局**（11 种）：
| 布局名称 | 用途 | 特点 |
|----------|------|------|
| Header Counter Two Column | 带计数器的双栏 | 顶部计数器 + 左图右文 |
| Chart Left Text Right | 左图表右文本 | 标准对比布局 |
| Contact | 联系页 | 联系方式展示 |
| Heading Bullet Image Description | 标题要点图 | 标题 + 要点 + 配图 |
| Icon Bullet Description | 图标要点 | 图标 + 要点 + 描述 |
| Icon Image Description | 图标图片 | 图标 + 图片 + 描述 |
| Image List With Description | 图片列表 | 纵向图片列表 |
| Metrics Description | 指标描述 | 指标 + 详细解释 |
| Numbered Bullet Single Image | 编号要点单图 | 编号列表 + 单图 |
| Table Of Contents | 目录 | 标准目录页 |
| Visual Metrics | 可视化指标 | 图表化指标展示 |

**适用场景**：
- 政府/机构汇报
- 学术演示
- 正式商务会议
- 合规/审计报告

---

### 3.2 Neo Standard（新版标准）
**定位**：现代版标准模板，融合传统与数据可视化

**设计风格**：
- 字体：Playfair Display + Open Sans
- 配色：深绿色系 (#1F8A2E)，更专业的墨绿色
- 特点：保留正式感的同时增强数据展示能力

**特色布局**（17 种）：
| 布局名称 | 用途 | 特点 |
|----------|------|------|
| Title Badge Chart | 徽章图表 | 标题 + 分类徽章 + 图表（支持 13 种图表类型） |
| Title Description Bullet List | 标题描述列表 | 左标题 + 右 bullet 列表 |
| Title Description Contact Cards | 联系卡片 | 联系人卡片网格 |
| Title Description Icon List | 图标列表 | 图标 + 文字列表 |
| Title Description Radial Cards | 径向卡片 | 圆形辐射布局卡片 |
| Title Description Timeline | 时间轴 | 水平时间线 |
| Title Dual Charts Comparison | 双图表对比 | 并排图表对比 |
| Title KPI Grid | KPI 网格 | 多指标 KPI 矩阵 |
| Title Metrics Chart | 指标图表 | 指标 + 图表组合 |
| Title Metrics Image | 指标图片 | 指标 + 配图 |
| Title Points Donut Grid | 环形图网格 | 多环形图组合 |

**适用场景**：
- 金融机构报告
- 可持续发展报告 (ESG)
- 董事会汇报
- 投资者关系演示

---

## 4. Swift（快速模板系列）

### 4.1 Swift（普通版）
**定位**：极简快速演示模板，适合敏捷演示

**设计风格**：
- 字体：Albert Sans（简洁无衬线字体）
- 配色：青色系 (#BFF4FF)，清新明快
- 特点：布局简洁，信息密度低，易于快速阅读

**核心布局**（9 种）：
| 布局名称 | 用途 | 特点 |
|----------|------|------|
| Intro Slide | 封面页 | 极简设计，标题 + 副标题 |
| Bullets With Icons Title Description | 图标要点 | 图标 + 要点 + 标题描述 |
| Icon Bullet List Description | 图标列表 | 图标列表 + 描述 |
| Image List Description | 图片列表 | 图片 + 描述 |
| Metrics Numbers | 数字指标 | 大数字展示 |
| Simple Bullet Points | 简单要点 | 纯文本要点列表 |
| Table Of Contents | 目录 | 简洁目录 |
| Table or Chart | 表格或图表 | 单一数据展示 |
| Timeline | 时间轴 | 简洁时间线 |

**适用场景**：
- 站立会议 (Standup)
- 快速更新 (Quick Update)
- 内部分享
- 敏捷演示

---

### 4.2 Neo Swift（新版快速）
**定位**：增强版快速模板，在简洁基础上增加数据展示

**设计风格**：
- 字体：Albert Sans
- 配色：青蓝色系 (#9CE0EE)，更鲜明的科技蓝
- 特点：保持简洁的同时支持复杂数据可视化

**特色布局**（16 种）：
| 布局名称 | 用途 | 特点 |
|----------|------|------|
| Title Centered Chart | 居中图表 | 大标题 + 居中主图表（支持 13 种图表类型） |
| Title Chart Metrics Sidebar | 图表侧边指标 | 图表 + 侧边指标栏 |
| Title Description Bullet List | 标题描述列表 | 左标题描述 + 右 bullet 列表 |
| Title Description Data Table | 数据表格 | 标题 + 数据表格 |
| Title Description Metrics Grid | 指标网格 | 2x2 或 3x3 指标网格 |
| Title Description Metrics Grid Image | 指标网格配图 | 指标 + 配图组合 |
| Title Dual Comparison Blocks | 双块对比 | 左右两大块对比 |
| Title Label Description Stat Cards | 统计卡片 | 标签 + 统计卡片组 |
| Title Subtitle Team Member Cards | 团队成员 | 标题 + 成员卡片 |
| Title Tagline Description Numbered Steps | 编号步骤 | 带标语的步骤流程 |
| Title Three By Three Metrics Grid | 3x3 指标网格 | 九宫格指标 |
| Title Description Six Charts Grid | 六图表网格 | 2x3 图表组合 |
| Title Description Six Charts Four Metrics | 六图表四指标 | 图表 + 指标混合 |
| Title Description Four Charts Six Bullets | 四图表六要点 | 图表 + 要点混合 |

**适用场景**：
- 技术分享
- 数据分析简报
- 产品迭代汇报
- OKR/KPI 回顾

---

## 模板选择建议

### 按演示类型选择

| 演示类型 | 推荐模板 | 理由 |
|----------|----------|------|
| 融资路演 | Modern / Neo Modern | 专业路演风格，投资人友好 |
| 年度报告 | General / Neo General | 通用性强，数据展示丰富 |
| 董事会汇报 | Standard / Neo Standard | 正式稳重，可信度高 |
| 内部周会 | Swift / Neo Swift | 简洁快速，信息密度适中 |
| 数据分析 | Neo General / Neo Modern | 多图表组合，可视化强 |
| 产品介绍 | Modern / Neo Swift | 视觉吸引力强 |
| 团队展示 | General / Neo Swift | 团队布局完善 |
| 战略规划 | Neo Standard / Neo General | 时间轴、对比布局丰富 |

### 按行业选择

| 行业 | 推荐模板 | 理由 |
|------|----------|------|
| 科技/互联网 | Neo Modern / Neo Swift | 现代科技感 |
| 金融/投资 | Standard / Neo Standard | 稳重可信 |
| 咨询/服务 | General / Neo General | 专业通用 |
| 医疗/健康 | Modern / Standard | 清晰专业 |
| 教育/学术 | Standard | 正式严谨 |
| 创意/设计 | Neo General / Neo Modern | 视觉创新 |

---

## 技术特性

### 字体系统
所有模板均使用 CSS 变量系统，支持自定义字体：
- `--heading-font-family`: 标题字体
- `--body-font-family`: 正文字体

### 颜色系统
每个模板组都有完整的颜色变量系统：
- `--background-color`: 背景色
- `--background-text`: 主要文字色
- `--primary-color`: 主题色
- `--primary-text`: 主题文字色（通常为反白）
- `--card-color`: 卡片背景色
- `--stroke`: 边框/分割线色

### 图表系统
Neo 系列模板支持 13 种图表类型：
- Bar / Horizontal Bar / Grouped / Stacked / Clustered / Diverging
- Line / Area / Area Stacked
- Pie / Donut
- Scatter

### 响应式设计
所有模板均基于 1280x720 (16:9) 画布设计，使用 Tailwind CSS 实现响应式布局。

---

## 总结

Presenton 的 8 套模板组覆盖了从正式到休闲、从数据密集到简洁快速的各种演示场景：

1. **General 系列**：最通用，适合大多数商务场景
2. **Modern 系列**：路演和融资演示首选
3. **Standard 系列**：正式场合和传统行业
4. **Swift 系列**：快速内部演示和敏捷团队

每个系列的 "Neo" 变体都在原有基础上增加了更丰富的数据可视化能力和现代设计元素，适合需要展示复杂数据的场景。
