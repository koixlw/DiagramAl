# DiagramAI

AI 驱动的智能图表生成工具，支持自然语言、代码和对话式交互，自动生成流程图和 E-R 图。

## 功能特性

### 流程图
- **三种输入方式**：自然语言描述、代码粘贴、AI 对话
- **标准图形**：开始/结束（圆角矩形）、处理（矩形）、判断（菱形）、输入/输出（平行四边形）、连接符（圆）
- **智能布局**：ELK.js 自动布局，端口级连线路由
- **全节点拖拽**：所有节点和标签可自由拖动
- **导出**：支持 SVG 和 PNG 导出

### E-R 图
- **三种输入方式**：自然语言描述、SQL 建表语句、AI 对话
- **Chen 标准**：实体（矩形）、关系（菱形）、属性（椭圆）、主键下划线、基数标注
- **智能布局**：BFS 分层 + 力导向微调，6+ 实体自动切换分层布局
- **自定义样式**：5 种预设主题 + 自定义颜色选择器
- **全节点拖拽**：实体、属性、关系、基数标注均可拖动
- **导出**：支持 SVG 和 PNG 导出

### 模板库
- 6 个流程图模板（质数判断、用户登录、冒泡排序、文件处理、订单处理、数据验证）
- 6 个 E-R 图模板（学生选课、电商系统、博客系统、图书管理、员工管理、医院系统）
- 一键加载，自动生成图表

### AI 对话模式
- 多轮交互，逐步构建和修改图表
- 支持增量修改："加一个判断节点"、"改成循环"、"把关系改成一对多"
- 对话历史自动保存

### 其他
- 对话历史（localStorage，最多 20 条）
- 页面缓存（keep-alive，切换不丢失）
- 缩放居中
- 暗色/亮色样式预设
- 设置页（API 配置、数据管理）
- 使用文档

## 技术栈

**前端**
- Vue 3 + Vite
- Vue Router
- D3.js（力导向布局、拖拽）
- ELK.js（流程图布局）
- Tailwind CSS

**后端**
- FastAPI
- Anthropic Claude API
- Pydantic 数据验证

## 快速开始

### 环境要求
- Node.js >= 18
- Python >= 3.10

### 安装

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 配置

创建 `.env` 文件：

```env
API_KEY=your_api_key
BASE_URL=http://127.0.0.1:8000/api
MODEL=claude-sonnet-4-20250514
```

### 运行

```bash
# 启动后端
cd backend
uvicorn main:app --reload

# 启动前端
cd frontend
npm run dev
```

## 项目结构

```
e:/ER-PROGRAM/
── backend/
│   ├── main.py              # FastAPI 应用
│   ├── schemas.py           # Pydantic 模型
│   ├── prompt_engine.py     # AI 系统提示词
│   └── requirements.txt     # Python 依赖
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Workspace.vue    # 工作台首页
│   │   │   ├── Flowchart.vue    # 流程图页
│   │   │   ├── ERDiagram.vue    # E-R 图页
│   │   │   ├── Templates.vue    # 模板库
│   │   │   ├── Settings.vue     # 设置页
│   │   │   └── Docs.vue         # 文档页
│   │   ├── router/
│   │   │   ── index.js         # 路由配置
│   │   ├── assets/
│   │   │   └── main.css         # 全局样式
│   │   ├── App.vue              # 根组件
│   │   └── main.js              # 入口
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
└── .env
```

## 使用示例

### 流程图 - 自然语言
```
用户登录流程：输入用户名和密码，验证格式是否正确，
如果格式错误则提示重新输入，如果格式正确则查询
数据库验证密码，密码正确则登录成功进入主页，
密码错误则提示密码错误
```

### 流程图 - 代码
```python
def is_prime(n):
    if n <= 1: return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0: return False
    return True
```

### E-R 图 - SQL
```sql
CREATE TABLE 学生 (
  学号 VARCHAR(20) PRIMARY KEY,
  姓名 VARCHAR(50),
  邮箱 VARCHAR(100)
);

CREATE TABLE 课程 (
  课程号 VARCHAR(20) PRIMARY KEY,
  名称 VARCHAR(100),
  学分 INT
);

CREATE TABLE 选课 (
  学号 VARCHAR(20),
  课程号 VARCHAR(20),
  选课日期 DATE,
  成绩 DECIMAL(5,2),
  PRIMARY KEY (学号, 课程号),
  FOREIGN KEY (学号) REFERENCES 学生(学号),
  FOREIGN KEY (课程号) REFERENCES 课程(课程号)
);
```

### E-R 图 - 对话模式
```
第一轮：学生选课系统：学生有学号、姓名、邮箱；
       课程有课程号、名称、学分；
       学生和课程是多对多的选课关系

第二轮：加一个教师实体，有工号、姓名、职称

第三轮：把学生和课程的关系改成通过选课表关联，
       选课表包含成绩和选课日期
```

## 许可证

MIT
