# 流程图 + ER 图智能体 - 实现计划

## Context
用户需要一个基于 AI 的智能体，能够接收自然语言描述，自动生成标准的**程序流程图**和**ER 图**，以 SVG/HTML 可交互图形的形式在 Web 界面中展示和下载。

## 架构

```
用户浏览器 (HTML + Tailwind + JS)
    ↕ POST /api/generate
FastAPI 后端 (Python)
    ↕ OpenAI API (gpt-4o, Structured Outputs)
返回结构化 JSON → 前端渲染 SVG
```

**核心设计思路**: AI 负责理解自然语言、输出结构化数据（节点/关系），前端负责布局和渲染。AI 不做空间定位（它不擅长），布局交给成熟算法（Dagre 做流程图层次布局、D3 force 做 ER 图力导向布局）。

## 项目结构

```
e:/ER-PROGRAM/
├── backend/
│   ├── main.py              # FastAPI 应用，3 个 API 端点
│   ├── schemas.py           # Pydantic 模型 + OpenAI JSON Schema
│   ├── prompt_engine.py     # AI 系统提示词模板
│   └── requirements.txt     # Python 依赖
├── frontend/
│   └── index.html           # 单文件前端应用（HTML + Tailwind + JS）
├── .env.example             # 环境变量模板
└── README.md                # 使用说明
```

## 关键设计

### 1. AI 输出 JSON Schema

**流程图**: `{ nodes: [{id, type, label}], edges: [{from, to, label}] }`
- node type: `start`/`end`(圆角矩形), `process`(矩形), `decision`(菱形), `io`(平行四边形), `connector`(圆)

**ER 图**: `{ entities: [{id, name, attributes: [{name, is_primary_key}]}], relationships: [{id, name, from_entity, to_entity, from_cardinality, to_cardinality, attributes}] }`
- 实体: 矩形 | 联系: 菱形 | 属性: 椭圆 | 主键: 下划线 | 基数: 1/N/M 标注

### 2. 布局策略
- **流程图**: 使用 Dagre 库做层次布局，自动计算节点位置，避免重叠
- **ER 图**: 使用 D3 force-simulation 做力导向布局，运行 300 次 tick 后取最终位置

### 3. SVG 渲染
纯手工创建 SVG 元素（不用重型库），根据布局坐标绘制：
- `<rect>`, `<polygon>`, `<ellipse>`, `<circle>`, `<path>` + `<text>` + arrow markers

### 4. 前端 CDN 依赖
- Tailwind CSS: `cdn.tailwindcss.com`
- Dagre: `cdn.jsdelivr.net/npm/dagre@0.8.5`
- D3: `cdn.jsdelivr.net/npm/d3@7`

### 5. 后端依赖
- fastapi, uvicorn, openai, python-dotenv, pydantic

## 实现步骤

### 第 1 步: 项目骨架
创建目录结构、`requirements.txt`、`.env.example`

### 第 2 步: 后端 - Schema 定义 (`backend/schemas.py`)
定义 Pydantic 请求/响应模型，以及 OpenAI Structured Outputs 用的 JSON Schema

### 第 3 步: 后端 - 提示词引擎 (`backend/prompt_engine.py`)
编写流程图和 ER 图的系统提示词，包含严格的输出规则

### 第 4 步: 后端 - API 端点 (`backend/main.py`)
实现 `POST /api/generate`、`POST /api/regenerate`、`GET /api/health`，对接 OpenAI API

### 第 5 步: 前端 - UI 框架 (`frontend/index.html`)
使用 Tailwind 搭建界面：类型选择器、文本输入区、生成按钮、SVG 展示区、下载按钮、状态提示

### 第 6 步: 前端 - API 对接
实现 fetch 调用、loading 状态、错误处理

### 第 7 步: 前端 - 流程图渲染
Dagre 布局 + SVG 手工绘制五种图形 + 箭头连线 + 分支标签

### 第 8 步: 前端 - ER 图渲染
D3 force 布局 + SVG 手工绘制实体/联系/属性 + 连线 + 基数标注 + 主键下划线

### 第 9 步: 前端 - 下载功能 + 完善
SVG 导出下载、PNG 导出下载、README 文档

## 验证方式
1. 启动后端: `uvicorn backend.main:app --reload`
2. 打开前端 HTML 页面
3. 输入流程图描述（如"判断一个数是否为质数的流程"），选择流程图，点击生成 → 检查 SVG 是否正确渲染
4. 输入 ER 图描述（如"学生选课系统：学生有学号、姓名、邮箱；课程有课程号、名称、学分；学生和课程是多对多选课关系，包含选课日期和成绩"），选择 ER 图，点击生成 → 检查实体、联系、属性、基数标注是否正确
5. 测试下载 SVG/PNG 功能
